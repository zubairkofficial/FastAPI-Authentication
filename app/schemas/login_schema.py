from pydantic import BaseModel, EmailStr, Field
from app.models.User import User


class LoginResponse(BaseModel):
    message: str
    user: User
    access_token: str
    refresh_token: str
    token_type: str
