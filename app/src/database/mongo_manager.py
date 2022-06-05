import logging
from typing import Optional

import pymongo
from bson import ObjectId
from database import UserSecurity
from database.database_manager import DatabaseManager
from database.exceptions import UsernameAlreadyExists
from fastapi import Depends
from models.token import Token
from models.user import User, UserInDB, UserOutDB
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
        self.db = self.client.users

        # create username unique index
        self.db.create_collection("user")
        self.db.user.create_index("username", unique=True)

        log.info("Connected to MongoDB.")

    async def close_database_connection(self):
        log.info("Closing connection with MongoDB.")
        self.client.close()
        log.info("Closed connection with MongoDB.")

    async def create_user(self, user: UserInDB):
        try:
            await self.db.user.insert_one(user.dict())
        except pymongo.errors.DuplicateKeyError:
            raise UsernameAlreadyExists(f"Username already exists")

    async def authenticate_user(self, username: str, password: str):
        user = await self.db.user.find_one({"username": username})
        if not user:
            return False
        user = UserInDB(**user)
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    async def get_access_token(self, username: str, password: str) -> Optional[Token]:
        user = await self.authenticate_user(username, password)
        if not user:
            return None
        token = self.create_access_token(user.username)
        return token

    async def get_current_user(self, current_username: str) -> UserOutDB:
        current_user = await self.db.user.find_one({"username": current_username})
        return UserOutDB(**current_user)
