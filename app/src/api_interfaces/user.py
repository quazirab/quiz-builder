import jwt
from api_interfaces.api_router import AppRouter
from database import get_database
from database.database_manager import DatabaseManager
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from models.token import Token
from models.user import CreateUser, UserInDB
from passlib.hash import bcrypt

user_router = AppRouter()


@user_router.get("/")
async def root():
    return "ok"


@user_router.post(
    "/user", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def create_user(user: CreateUser, db: DatabaseManager = Depends(get_database)):
    user = UserInDB(username=user.username, hashed_password=bcrypt.hash(user.password))
    await db.create_user(user)


@user_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DatabaseManager = Depends(get_database),
):
    token = await db.get_access_token(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
