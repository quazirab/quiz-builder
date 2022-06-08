from models.pyobjectid import PydanticObjectId
from pydantic import BaseModel, conlist, constr, validator


class Quiz(BaseModel):
    title: constr(strip_whitespace=True)
    questions: conlist(constr(strip_whitespace=True), min_items=1, max_items=10)
    answers: conlist(constr(strip_whitespace=True), min_items=1, max_items=5)

    class Config:
        orm_mode = True

    # TODO validator for answers exists in question
    @validator("answers", pre=False)
    def answers_in_question(cls, v, values, **kwargs):
        questions = values["questions"]
        answers = v
        if len(answers) != len(set(answers)):
            raise ValueError('Answers are not unique')

        for answer in answers:
            if answer not in questions:
                raise ValueError(f"{answer} does not exists in questions")
        return v

class QuizInDB(Quiz):
    owner_id: str

class QuizUpdate(Quiz):
    id: PydanticObjectId
