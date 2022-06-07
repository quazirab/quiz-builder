import logging
from typing import Optional

import pymongo
from bson import ObjectId
from database import DatabaseManager, UserSecurity
from database.exceptions import UsernameAlreadyExists
from fastapi import Depends
from models import (CreateUserHashed, Quiz, QuizInDB, Token, UserInDBwID,
                    UserOutDB)
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from passlib.context import CryptContext

log = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MongoManager(DatabaseManager, UserSecurity):
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(self, path: str):
        log.info("Connecting to MongoDB.")
        self.client = AsyncIOMotorClient(path, maxPoolSize=10, minPoolSize=10)
        self.db = self.client.quiz

        # create username unique index
        list_collection_names = await self.db.list_collection_names()
        if "user" not in list_collection_names:
            await self.db.create_collection("user")
            await self.db.user.create_index("username", unique=True)

        if "published_quiz" not in list_collection_names:
            await self.db.create_collection("published_quiz")

        if "unpublished_quiz" not in list_collection_names:
            await self.db.create_collection("unpublished_quiz")

        log.info("Connected to MongoDB.")

    async def close_database_connection(self):
        log.info("Closing connection with MongoDB.")
        self.client.close()
        log.info("Closed connection with MongoDB.")

    async def create_user(self, user: CreateUserHashed):
        try:
            await self.db.user.insert_one(user.dict())
        except pymongo.errors.DuplicateKeyError:
            raise UsernameAlreadyExists(f"Username already exists")

    async def authenticate_user(self, username: str, password: str):
        user = await self.db.user.find_one({"username": username})
        if not user:
            return False
        user = UserInDBwID(**user)
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    async def get_access_token(self, username: str, password: str) -> Optional[Token]:
        user = await self.authenticate_user(username, password)
        if not user:
            return None
        token = self.create_access_token(user.id)
        return token

    async def get_current_user(self, current_user_id: str) -> UserOutDB:
        current_user = await self.db.user.find_one(ObjectId(current_user_id))
        return UserOutDB(**current_user)

    async def create_quiz(self, current_user_id: str, quiz: Quiz):
        current_user = await self.get_current_user(current_user_id)
        quiz_in_db = QuizInDB(**quiz.dict(), owner_id=current_user_id)
        quiz_id = await self.db.unpublished_quiz.insert_one(quiz_in_db.dict())

        current_user.unpublished_quiz.append(quiz_id.inserted_id)

        await self.db.user.update_one(
            {"_id": ObjectId(current_user_id)}, {"$set": current_user.dict()}
        )
