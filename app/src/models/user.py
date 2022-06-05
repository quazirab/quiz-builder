from pydantic import BaseModel, validator


class User(BaseModel):
    username: str


class CreateUser(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str
