from database.database_manager import DatabaseManager
from database.mongo_manager import MongoManager

db = MongoManager()


async def get_database() -> DatabaseManager:
    return db
