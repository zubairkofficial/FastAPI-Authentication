import jwt
from typing import Union
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.db.database import get_db
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
from app.models.User import User

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expire_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



class TokenData(BaseModel):
    email: Union[str, None] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, messsage="Could not valid Credentails", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        return user
    except InvalidTokenError:
        raise credentials_exception
    
    

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.email_verified_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, messsage="User not Verified")
    return current_user