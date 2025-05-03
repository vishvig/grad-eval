from pydantic import BaseModel
from typing import Optional, Dict, Any


class AuthResponse(BaseModel):
    status: str
    message: str
    body: Dict[str, Any]  # Will contain authenticated, user_id, assessment_status, and assessment_start_time


class CaptchaResponse(BaseModel):
    status: str
    message: str
    body: Dict[str, str]  # Will contain the base64 image and session_id 


class VerifyResponse(BaseModel):
    status: str
    message: str
    user_id: str
