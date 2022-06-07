from abc import abstractmethod
from typing import List

from models import CreateUserHashed, UserOutDB


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
