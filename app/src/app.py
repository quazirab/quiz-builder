import logging
import sys

import uvicorn
from api_interfaces import user_router
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from models import User
from tortoise.contrib.fastapi import register_tortoise

from utils.environment import os_environment
from utils.logger import init_logging
from utils.signal_handler import load_signal_handler

routers = [user_router]

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


def setup_routers(app, routers):
    for router in routers:
        router.jwt_secret = os_environment("JWT_SECRET", "myjwtsecret")
        router.user = User
        app.include_router(router)


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

    # register database
    register_tortoise(
        app,
        db_url="sqlite://db.sqlite3",
        modules={"models": ["models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    # start server
    uvicorn.run(
        "__main__:app",
        host=os_environment("APP_HOST", "0.0.0.0"),
        port=os_environment("APP_PORT", 5001),
    )
