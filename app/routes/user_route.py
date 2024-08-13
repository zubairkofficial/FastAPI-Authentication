from fastapi import APIRouter, status, Depends, HTTPException
from app.db.database import get_db
from app.schemas.user_schema import RegisterUser, LoginUser, resetPassword
from app.models.User import User
from sqlalchemy.orm import Session
from app.utils.security import hashed_password, verify_password
from app.utils.OAuth import create_access_token
from app.utils.smtp import send_verification_email, send_reset_password
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy import func
import uuid
import random
from app.models.PasswordReset import PasswordReset
from datetime import datetime, timedelta

router = APIRouter()
SECRET_KEY = "Cyberify@24"
serializer = URLSafeTimedSerializer(SECRET_KEY)

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(user: RegisterUser, db: Session = Depends(get_db)):
    hash_password = hashed_password(user.password)
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return {'status':'error', 'message':"Email Already Exists"}
    
    new_user = User(name=user.name, email=user.email, password=hash_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate a token
    token = serializer.dumps(user.email, salt="email-confirm")
    activation_link = f"http://localhost:8000/api/auth/active-user?token={token}"
    
    # Send verification email
    send_verification_email(user.email, activation_link)
    
    return {"message": "User Created Successfully. Please check your email for activation link.", "User": new_user}



@router.get('/active-user')
async def active_user(token: str, db: Session = Depends(get_db)):
    try:
        # Decode the token to get the email
        email = serializer.loads(token, salt="email-confirm", max_age=3600)  # Token valid for 1 hour
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, messsage="The link has expired")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, messsage="Invalid token")

    # Find the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="User not found")

    # Activate the user
    if user.email_verified_at:
        return {"message": "User already Verified"}

    user.email_verified_at = func.now()
    db.commit()
    return {"message": "User Verified successfully"}



@router.post('/login', status_code=status.HTTP_202_ACCEPTED)
async def login(user: LoginUser, db: Session = Depends(get_db)):
    print(f"user: {user}")
    print(f"Type of User: {type(user)}")
    print(f"user email: {user.email}")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="User not found")
    if db_user and verify_password(user.password, db_user.password):
        if not db_user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, messsage="User not verified")

        access_token = create_access_token(data={"id": db_user.id})
        return {"message": "Login Successfully","user":db_user, "token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="Invalid Credentials")



from pydantic import EmailStr
@router.post('/forgot-password', status_code=status.HTTP_200_OK)
async def forget_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="Invalid Email")
    
    token = serializer.dumps(email, salt="password-reset")
    random_password = random.randint(100000, 999999)

    send_reset_password(email, random_password)
    reset_code_expiry = datetime.utcnow() + timedelta(hours=1)
    reset_entry = PasswordReset(user_id=user.id, reset_code=random_password, reset_expiry=reset_code_expiry)
    db.add(reset_entry)
    db.commit()
    db.refresh(reset_entry)

    return {"message": "Password reset link sent to your email"}



@router.post('/reset-password', status_code=status.HTTP_200_OK)
def reset_password(req: resetPassword, db: Session= Depends(get_db)):
    user = db.query(User).filter(User.email==req.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="Invalid Email")
    reset_entry = db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id,
        PasswordReset.reset_code == req.reset_code,
        ).first()
    
    # print(f"id: {reset_entry.user_id}, reset_code: {reset_entry.reset_code}, expiry: {reset_entry.reset_expiry}")
    
    if not reset_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, messsage="Invalid or Expire reset code")
    
    hash_password = hashed_password(req.new_password)
    user.password = hash_password
    db.delete(reset_entry)
    db.commit()

    return {"message": "Password has been reset successfully"}