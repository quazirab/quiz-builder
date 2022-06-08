from api_interfaces.api_router import AppRouter
from database import DatabaseManager, UserSecurity, get_database
from fastapi import Depends, HTTPException, Request, Response, status
from models.user import CreateUser, CreateUserHashed, User, UserOutDB
from passlib.hash import bcrypt

user_router = AppRouter(tags=["user"],prefix="/user")



@user_router.post(
    "", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def create_user(user: CreateUser, db: DatabaseManager = Depends(get_database)):
    user = CreateUserHashed(
        username=user.username, hashed_password=bcrypt.hash(user.password)
    )
    await db.create_user(user)


@user_router.get("", response_model=UserOutDB)
async def current_user(
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    return await db.get_current_user(current_user_id=current_user_id)
