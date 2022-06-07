from database.database_manager import DatabaseManager
from database.user_security import UserSecurity

from database.mongo_manager import MongoManager  # isort:skip

db = MongoManager()


async def get_database() -> DatabaseManager:
    return db
