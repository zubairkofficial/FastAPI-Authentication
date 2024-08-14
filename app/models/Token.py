from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.db.database import Base, engine
import datetime

from sqlalchemy.orm import relationship


class Token(Base):
    __tablename__ = "token"
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token = Column(String(500), primary_key=True)
    refresh_token = Column(String(500), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
    user = relationship("User", backref="tokens")
