from pydantic import BaseModel


class ChatResponse(BaseModel):
    user_id: str
    question_id: str
    response: str  # Will contain markdown response 