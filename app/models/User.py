from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from app.db.database import Base, engine
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(25), nullable=False)
    lastName = Column(String(25), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    type = Column(String(25), nullable=False, default='user')
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    Created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

