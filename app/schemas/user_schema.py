from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str

class resetPassword(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str
