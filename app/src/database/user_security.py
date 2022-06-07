from datetime import datetime, timedelta

from bson import ObjectId
from database.exceptions import CredentialsException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.token import Token, TokenData
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserSecurity:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(user_id: str) -> Token:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user_id}
        if access_token_expires:
            expire = datetime.utcnow() + access_token_expires
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=encoded_jwt, token_type="bearer")

    @staticmethod
    async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise CredentialsException("Could not validate credentials")
            token_data = TokenData(user_id=user_id)
        except JWTError:
            raise CredentialsException("Could not validate credentials")
        return token_data.user_id
