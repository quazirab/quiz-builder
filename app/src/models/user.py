from pydantic import BaseModel


class User(BaseModel):
    username: str


class CreateUser(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str


class UserOutDB(User):
    username: str
    unpublished_quiz: list[int] | None
    published_quiz: list[int] | None
