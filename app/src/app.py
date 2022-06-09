import logging
import sys

import uvicorn
from api_interfaces.quiz import quiz_creator_router, quiz_player_router
from api_interfaces.user import user_router
from database import DatabaseManager, db, get_database
from database.exceptions import (CredentialsException, QuizPlayerFailed,
                                 UsernameAlreadyExists, UserNotAllowed)
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models import Token

from utils.environment import os_environment
from utils.logger import init_logging
from utils.signal_handler import load_signal_handler

routers = [user_router, quiz_creator_router, quiz_player_router]

app = FastAPI()


@app.exception_handler(UsernameAlreadyExists)
async def username_exception_handler(
    request: Request, exception: UsernameAlreadyExists
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(CredentialsException)
async def username_exception_handler(request: Request, exception: CredentialsException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exception)}
    )


@app.exception_handler(UserNotAllowed)
async def username_exception_handler(request: Request, exception: UserNotAllowed):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exception)}
    )

@app.exception_handler(QuizPlayerFailed)
async def username_exception_handler(request: Request, exception: QuizPlayerFailed):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exception)}
    )

@app.get("/")
async def root():
    return "ok"

@app.post("/token", response_model=Token)
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


def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


def setup_routers(app, routers):
    for router in routers:
        app.include_router(router)


@app.on_event("startup")
async def startup():
    await db.connect_to_database(path=os_environment("DB_PATH", None))


@app.on_event("shutdown")
async def shutdown():
    await db.close_database_connection()


if __name__ == "__main__":
    # load signal handlers
    load_signal_handler(signal_handler)
    init_logging(
        level=os_environment("LOG_LEVEL", "DEBUG"),
        slack_hook=os_environment("SLACK_HOOK", None),
    )
    logger = logging.getLogger("controller")

    # setup routers
    setup_routers(app, routers)

    # start server
    uvicorn.run(
        "__main__:app",
        host=os_environment("APP_HOST", "0.0.0.0"),
        port=int(os_environment("APP_PORT", 5000)),
    )
