# app/models/user.py
from sqlalchemy import Boolean, Column, String, DateTime, Text
from datetime import datetime

from app.db.base_class import Base


class User(Base):
    """User model."""
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)