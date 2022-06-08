import logging
from typing import Optional

import pymongo
from bson import ObjectId
from database import DatabaseManager, UserSecurity
from database.exceptions import UsernameAlreadyExists, UserNotAllowed
from fastapi import Depends
from models import (CreateUserHashed, Quiz, QuizInDB, QuizUpdate, Token,
                    UserInDBwID, UserOutDB)
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

        if current_user.unpublished_quiz is None :
            current_user.unpublished_quiz = []
        current_user.unpublished_quiz.append(quiz_id.inserted_id)

        await self.db.user.update_one(
            {"_id": ObjectId(current_user_id)}, {"$set": current_user.dict()}
        )

    async def get_quiz(self, current_user_id: str, quiz_id: str) -> Quiz:
        user_quizes = await self.db.user.find_one(ObjectId(current_user_id), {"unpublished_quiz":1, "published_quiz":1})
        quiz_id_obj = ObjectId(quiz_id)
        collection = None
        if quiz_id_obj in user_quizes["unpublished_quiz"] :
            collection = "unpublished_quiz"
        elif quiz_id_obj in  user_quizes["published_quiz"]:
            collection = "published_quiz"
        else:
            raise UserNotAllowed(f"User not allowed to read the quiz")
        quiz = await self.db[collection].find_one(quiz_id_obj)
        return Quiz(**quiz)


    async def update_quiz(self, current_user_id: str, quiz: QuizUpdate):
        # find all the unpublished quizes by the current user
        user_unpublished_quizes = await self.db.user.find_one(ObjectId(current_user_id), {"unpublished_quiz":1})
        quiz_id_obj = ObjectId(quiz.id)
        if quiz_id_obj not in user_unpublished_quizes["unpublished_quiz"]:
            raise UserNotAllowed(f"User not allowed to update the quiz")
        await self.db.unpublished_quiz.update_one({"_id": quiz_id_obj}, {"$set": quiz.dict(exclude={'id'})})


    async def publish_quiz(self, current_user_id: str, quiz_id:str):
        quiz_id_obj = ObjectId(quiz_id)
        user_id_obj = ObjectId(current_user_id)
        # get current user quizes
        user_quizes = await self.db.user.find_one(user_id_obj, {"unpublished_quiz":1, "published_quiz":1})

        # check if the current user owns the quiz in unpublished quiz
        if quiz_id_obj not in user_quizes["unpublished_quiz"]:
            raise UserNotAllowed(f"User does not have any unpublished quiz associated with that id")

        # add the unpublished quiz to published quiz collection
        quiz = await self.db.unpublished_quiz.find_one(quiz_id_obj)
        await self.db.published_quiz.insert_one(quiz)

        # remove it from unpublished quiz
        await self.db.unpublished_quiz.delete_one({"_id": quiz_id_obj})

        # update the user
        user_quizes["unpublished_quiz"].remove(quiz_id_obj)
        if user_quizes["published_quiz"] is None:
            user_quizes["published_quiz"] = []
        user_quizes["published_quiz"].append(quiz_id_obj)
        await self.db.user.update_one({"_id": user_id_obj}, {"$set": {"unpublished_quiz":user_quizes["unpublished_quiz"], "published_quiz": user_quizes["published_quiz"]}})

    async def delete_quiz(self, current_user_id: str, quiz_id: str) -> Quiz:
        user_id_obj = ObjectId(current_user_id)
        user_quizes = await self.db.user.find_one(user_id_obj, {"unpublished_quiz":1, "published_quiz":1})
        quiz_id_obj = ObjectId(quiz_id)
        collection = None
        if quiz_id_obj in user_quizes["unpublished_quiz"] :
            collection = "unpublished_quiz"
            user_quizes["unpublished_quiz"].remove(quiz_id_obj)
            _set = {"unpublished_quiz":user_quizes["unpublished_quiz"]}
        elif quiz_id_obj in  user_quizes["published_quiz"]:
            collection = "published_quiz"
            user_quizes["published_quiz"].remove(quiz_id_obj)
            _set = {"published_quiz":user_quizes["published_quiz"]}
        else:
            raise UserNotAllowed(f"User not allowed to read the quiz")

        #remove the quiz from the user
        await self.db.user.update_one({"_id": user_id_obj}, {"$set": _set})

        # delete the quiz from the collection
        await self.db[collection].delete_one({"_id": quiz_id_obj})
