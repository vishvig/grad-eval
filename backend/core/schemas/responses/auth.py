from pydantic import BaseModel
from typing import Optional, Dict


class AuthResponse(BaseModel):
    status: str
    message: str
    body: Optional[Dict] = None


class CaptchaResponse(BaseModel):
    status: str
    message: str
    body: Dict[str, str]  # Will contain the base64 image and session_id 


class VerifyResponse(BaseModel):
    status: str
    message: str
    user_id: str
