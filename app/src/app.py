import logging
import sys

import uvicorn
from api_interfaces.user import user_router
from database import db
from database.exceptions import UsernameAlreadyExists
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from utils.environment import os_environment
from utils.logger import init_logging
from utils.signal_handler import load_signal_handler

routers = [user_router]

app = FastAPI()


@app.exception_handler(UsernameAlreadyExists)
async def username_exception_handler(
    request: Request, exception: UsernameAlreadyExists
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


def setup_routers(app, routers):
    for router in routers:
        router.jwt_secret = os_environment("JWT_SECRET", "myjwtsecret")
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
        port=os_environment("APP_PORT", 5001),
    )
