from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    id: int
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class RegisterUser(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=10, max_length=255)
    password: str


class LoginUser(BaseModel):
    email: EmailStr = Field(min_length=10, max_length=255)
    password: str = Field(min_length=6, max_length=255)


class resetPassword(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str
