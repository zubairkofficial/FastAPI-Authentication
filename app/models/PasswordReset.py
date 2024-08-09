from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.User import User

class PasswordReset(Base):
    __tablename__ = 'password_reset'


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, )
    reset_code = Column(String(6), nullable=False)
    reset_expiry = Column(DateTime, nullable=False)


