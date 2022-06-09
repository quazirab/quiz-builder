from abc import abstractmethod
from typing import Optional

from models import (CreateUserHashed, CreateUserInsert, Quiz, QuizInDB,
                    QuizWithId, Solution, SubmitQuiz, Token, UserAllInfo,
                    UserInDBwID, UserOutDB)


class DatabaseManager(object):
    @property
    def client(self):
        raise NotImplementedError

    @property
    def db(self):
        raise NotImplementedError

    @abstractmethod
    async def connect_to_database(self, path: str):
        pass

    @abstractmethod
    async def close_database_connection(self):
        pass

    @abstractmethod
    async def create_user(self, user: CreateUserHashed):
        pass

    @abstractmethod
    async def get_current_user(self) -> UserOutDB:
        pass

    @abstractmethod
    async def authenticate_user(self, username: str, password: str):
        pass

    @abstractmethod
    async def get_access_token(self, username: str, password: str) -> Optional[Token]:
        pass

    @abstractmethod
    async def get_current_user(self, current_user_id: str) -> UserOutDB:
        pass

    @abstractmethod
    async def create_quiz(self, current_user_id: str, quiz: Quiz):
        pass

    @abstractmethod
    async def get_quiz(self, current_user_id: str, quiz_id: str) -> Quiz:
        pass

    @abstractmethod
    async def update_quiz(self, current_user_id: str, quiz: QuizWithId):
        pass

    @abstractmethod
    async def publish_quiz(self, current_user_id: str, quiz_id:str):
        pass

    @abstractmethod
    async def delete_quiz(self, current_user_id: str, quiz_id: str) -> Quiz:
        pass

    @abstractmethod
    async def play_quiz(self, current_user_id: str) -> QuizWithId:
        pass

    @abstractmethod
    async def submit_play_quiz(self, current_user_id: str, submitted_quiz: SubmitQuiz) -> int:
        pass

    @abstractmethod
    async def get_player_solution(self, current_user_id: str) -> list[Solution]:
        pass

    @abstractmethod
    async def get_creator_solution(self, current_user_id: str) -> list[Solution]:
        pass
