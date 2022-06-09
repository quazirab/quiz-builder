from api_interfaces.api_router import AppRouter
from database import DatabaseManager, UserSecurity, get_database
from fastapi import Depends, status
from models import Quiz, QuizWithId, QuizWithIdAnswers, Solution, SubmitQuiz

quiz_creator_router = AppRouter(tags=["quiz-creator"],prefix="/quiz/creator")
quiz_player_router = AppRouter(tags=["quiz-player"],prefix="/quiz/player")

#===========================Creator==============================

# create quiz
@quiz_creator_router.post("")
async def create_quiz(
    quiz: Quiz,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Create Quiz
    """
    await db.create_quiz(current_user_id=current_user_id, quiz=quiz)


# # update quiz
@quiz_creator_router.put("")
async def update_unpublished_quiz(
    quiz: QuizWithIdAnswers,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Update Unpublished Quiz
    """
    await db.update_quiz(current_user_id=current_user_id, quiz=quiz)

# get quiz
@quiz_creator_router.get("", response_model=Quiz)
async def update_unpublished_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Update unpublished quiz
    """
    return await db.get_quiz(current_user_id=current_user_id, quiz_id=quiz_id)


# publish quiz
@quiz_creator_router.post("/publish", status_code=status.HTTP_200_OK)
async def publish_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Publish Quiz
    """
    await db.publish_quiz(current_user_id=current_user_id, quiz_id=quiz_id)

# delete quiz
@quiz_creator_router.delete("", status_code=status.HTTP_200_OK)
async def delete_quiz(
    quiz_id: str,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Delete published quiz
    """
    await db.delete_quiz(current_user_id=current_user_id, quiz_id=quiz_id)

# Get Solutions
@quiz_creator_router.get("/solutions", response_model=list[Solution])
async def get_creator_solutions(
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database)
):
    """
    Submitted Solutions by the Player for the Creator
    """
    return await db.get_creator_solution(current_user_id=current_user_id)

#================================Player==================================

# Get quiz
@quiz_player_router.get("", response_model=QuizWithId)
async def get_quiz_to_play(
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Get quiz to play
    """
    return await db.play_quiz(current_user_id=current_user_id)

# Submit quiz
@quiz_player_router.post("")
async def submit_quiz_to_play(
    submitted_quiz: SubmitQuiz,
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database),
):
    """
    Submit quiz to play
    """
    return await db.submit_play_quiz(current_user_id=current_user_id, submitted_quiz=submitted_quiz)

# Get Solutions
@quiz_player_router.get("/solutions", response_model=list[Solution]|None)
async def get_player_solutions(
    current_user_id: str = Depends(UserSecurity.get_current_user_id),
    db: DatabaseManager = Depends(get_database)
):
    """
    Get solution for the submitted quiz
    """
    return await db.get_player_solution(current_user_id=current_user_id)
