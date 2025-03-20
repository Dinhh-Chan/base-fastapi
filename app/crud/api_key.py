from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import create_api_key
from app.crud.base import CRUDBase
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    def get_by_key(self, db: Session, *, key: str) -> Optional[APIKey]:
        """
        Get an API key by its value.
        """
        return db.execute(
            select(self.model).filter(self.model.key == key)
        ).scalars().first()

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[APIKey]:
        """
        Get multiple API keys for a user.
        """
        return db.execute(
            select(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def create_with_user(
        self, db: Session, *, obj_in: APIKeyCreate, user_id: int
    ) -> APIKey:
        """
        Create a new API key for a user.
        """
        key = create_api_key()
        
        db_obj = APIKey(
            key=key,
            name=obj_in.name,
            user_id=user_id,
            is_active=obj_in.is_active,
            expires_at=obj_in.expires_at,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_expiry(
        self, db: Session, *, obj_in: APIKeyCreate, user_id: int, days_valid: int = 30
    ) -> APIKey:
        """
        Create a new API key with an expiry date.
        """
        if not obj_in.expires_at:
            obj_in.expires_at = datetime.utcnow() + timedelta(days=days_valid)
        
        return self.create_with_user(db=db, obj_in=obj_in, user_id=user_id)

    def is_active(self, api_key: APIKey) -> bool:
        """
        Check if an API key is active.
        """
        return api_key.is_active and (api_key.expires_at is None or api_key.expires_at > datetime.utcnow())


crud_api_key = CRUDAPIKey(APIKey)