from pydantic import BaseModel


class GitlabAuthRequest(BaseModel):
    full_name: str
    token: str
    captcha_session_id: str
    captcha_text: str
