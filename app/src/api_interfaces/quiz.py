from api_interfaces.api_router import AppRouter
from database import DatabaseManager, UserSecurity, get_database
from fastapi import Depends, status
from models import Quiz, QuizUpdate

quiz_router = AppRouter()


# create quiz
@quiz_router.post("/quiz/creator")
async def create_quiz(
    quiz: Quiz,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    await db.create_quiz(current_user_id=current_user_id, quiz=quiz)


# # update quiz
@quiz_router.put("/quiz/creator")
async def update_unpublished_quiz(
    quiz: QuizUpdate,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    await db.update_quiz(current_user_id=current_user_id, quiz=quiz)

# get quiz
@quiz_router.get("/quiz/creator", response_model=Quiz)
async def update_unpublished_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    return await db.get_quiz(current_user_id=current_user_id, quiz_id=quiz_id)


# publish quiz
@quiz_router.post("/quiz/creator/publish", status_code=status.HTTP_200_OK)
async def publish_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    await db.publish_quiz(current_user_id=current_user_id, quiz_id=quiz_id)

# delete quiz
@quiz_router.delete("/quiz/creator", status_code=status.HTTP_200_OK)
async def delete_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    await db.delete_quiz(current_user_id=current_user_id, quiz_id=quiz_id)
