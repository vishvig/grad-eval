from pydantic import BaseModel
from typing import List, Optional, Dict


class DefaultResponse(BaseModel):
    status: str
    message: str
    body: Optional[Dict] = None


class NextQuestionResponseModel(BaseModel):
    id: str = None
    text: str = None
    lastQuestion: bool = False
    quizFinished: bool = False


class NextQuestionResponse(DefaultResponse):
    body: Optional[NextQuestionResponseModel] = None


class StartAssessmentResponse(DefaultResponse):
    body: Optional[List[NextQuestionResponseModel]] = None
