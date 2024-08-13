from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str


class RegisterUser(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=3, max_length=255)
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str

class resetPassword(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str
