from pydantic import BaseModel
from typing import List


class AnswerSubmission(BaseModel):
    questionId: str
    selectedAnswers: List[str]


class StartAssessmentRequest(BaseModel):
    user_id: str
