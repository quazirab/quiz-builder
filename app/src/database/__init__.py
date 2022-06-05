from database.database_manager import DatabaseManager
from database.mongo_manager import MongoManager
from database.user_security import UserSecurity

db = MongoManager()


async def get_database() -> DatabaseManager:
    return db
