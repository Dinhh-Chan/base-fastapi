from typing import Any
from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, func


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), 
                        onupdate=datetime.utcnow, nullable=False)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()