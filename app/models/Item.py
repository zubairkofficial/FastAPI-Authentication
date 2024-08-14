from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, func
from app.db.database import engine, Base
from sqlalchemy.orm import relationship


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    vocode_ai_id = Column(String(500))
    client_id = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    active = Column(Boolean)
    label = Column(String(500))
    inbound_agent = Column(String(500))
    outbound_only = Column(Boolean)
    example_context = Column(JSON)
    number = Column(String(25))
    telephony_provider = Column(String(255))
    telephony_account_connection = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
