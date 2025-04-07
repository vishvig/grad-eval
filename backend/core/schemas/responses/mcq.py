from pydantic import BaseModel
from typing import List, Optional, Dict


class DefaultResponse(BaseModel):
    status: str
    message: str
    body: Optional[Dict] = None


class MCQOption(BaseModel):
    id: str
    text: str


class NextQuestionResponseModel(BaseModel):
    id: str
    text: str
    options: List[MCQOption]
    allowMultiple: bool


class NextQuestionResponse(DefaultResponse):
    body: Optional[NextQuestionResponseModel] = None


class StartAssessmentResponse(DefaultResponse):
    body: Optional[List[NextQuestionResponseModel]] = None
