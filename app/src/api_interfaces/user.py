import jwt
from api_interfaces.api_router import AppRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User_Pydantic, UserIn_Pydantic

user_router = AppRouter()


async def authenticate_user(username: str, password: str):
    user = await user_router.user.get(username=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


@user_router.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), user_router.jwt_secret)

    return {"access_token": token, "token_type": "bearer"}
