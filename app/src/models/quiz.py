from pydantic import BaseModel, conlist


class Quiz(BaseModel):
    title: str
    questions: conlist(str, min_items=1, max_items=10)
    answers: conlist(str, min_items=1, max_items=5)

    class Config:
        orm_mode = True

    # TODO validator for answers exists in question


class QuizInDB(Quiz):
    owner_id: str
