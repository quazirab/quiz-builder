from api_interfaces.api_router import AppRouter
from database import DatabaseManager, UserSecurity, get_database
from fastapi import Depends
from models import Quiz

quiz_router = AppRouter()


# create quiz
@quiz_router.post("/quiz/creator")
async def current_user(
    quiz: Quiz,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    await db.create_quiz(current_user_id=current_user_id, quiz=quiz)


# update quiz


# publish quiz


# delete quiz
