from fastapi import APIRouter, status, Depends, HTTPException, Request, status
from app.db.database import get_db
from app.schemas.user_schema import RegisterUser, LoginUser, resetPassword, UserResponse
from app.models.User import User
from app.models.Token import Token
from sqlalchemy.orm import Session
from app.utils.security import hashed_password, verify_password
from app.utils.OAuth import create_access_token
from app.utils.OAuth import create_refresh_token
from app.utils.smtp import send_verification_email, send_reset_password
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy import func
import uuid
from pydantic import BaseModel
import random
from app.models.PasswordReset import PasswordReset
from datetime import datetime, timedelta
from app.schemas.token_schema import TokenSchema
from app.schemas.user_schema import BaseUser
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
SECRET_KEY = "Cyberify@24"
serializer = URLSafeTimedSerializer(SECRET_KEY)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(user: RegisterUser, db: Session = Depends(get_db)):
    hash_password = hashed_password(user.password)
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return {'status': 'error', 'message': "Email Already Exists"}

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


@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(user: LoginUser, db: Session = Depends(get_db)):
    print(f"user: {user}")
    print(f"Type of User: {type(user)}")
    print(f"user email: {user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="User not found")
    if db_user and verify_password(user.password, db_user.password):
        if not db_user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, message="User not verified")

        access_token = create_access_token(data={"id": db_user.id})
        refresh_token = create_refresh_token(data={"id": db_user.id})
        token_db = Token(user_id=db_user.id, access_token=access_token, refresh_token=refresh_token, status=True)
        db.add(token_db)
        db.commit()
        db.refresh(token_db)
        user_response = UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
        print(f"user: {user_response}")
        return {"message": "Login Successfully", "user": user_response, "access_token": access_token,
                "refresh_token": refresh_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="Invalid Credentials")


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
def reset_password(req: resetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    token_db = db.query(Token).filter(Token.access_token == token).first()
    if not token_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    db.delete(token_db)
    db.commit()
    return {"message": "Logged out successfully"}
