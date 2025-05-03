from pydantic import BaseModel
from typing import List


class NextQuestion(BaseModel):
    user_id: str


class AnswerSubmission(BaseModel):
    user_id: str
    question_id: str
    selected_answers: List[str]


class StartAssessmentRequest(BaseModel):
    user_id: str
    start_epoch: int  # Epoch time when assessment started
