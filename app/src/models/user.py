from bson import ObjectId
from models.pyobjectid import PydanticObjectId
from pydantic import BaseModel, Field


class User(BaseModel):
    username: str

    class Config:
        orm_mode = True


class CreateUser(User):
    password: str


class CreateUserHashed(User):
    hashed_password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UserInDBwID(CreateUserHashed):
    id: PydanticObjectId = Field(..., alias="_id")


class UserOutDB(User):
    unpublished_quiz: list[PydanticObjectId] | None = []
    published_quiz: list[PydanticObjectId] | None = []
    score: int = 0

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
