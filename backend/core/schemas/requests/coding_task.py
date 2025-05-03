from pydantic import BaseModel
from typing import Optional, Dict
from fastapi import UploadFile, File


class DownloadTaskFileRequest(BaseModel):
    user_id: str
    question_id: str


class NextTaskRequest(BaseModel):
    user_id: str
    current_epoch: int
    start_epoch: int
    question_id: Optional[str] = None


class NextTaskResponse(BaseModel):
    user_id: str
    question_id: Optional[str] = None
    body: Optional[str] = None


class StartAssessmentRequest(BaseModel):
    user_id: str
    start_epoch: int
