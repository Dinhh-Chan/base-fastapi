from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        return db.execute(
            select(self.model).filter(self.model.email == email)
        ).scalars().first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get a user by username.
        """
        return db.execute(
            select(self.model).filter(self.model.username == username)
        ).scalars().first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email_or_username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email/username and password.
        """
        # Try to authenticate with email
        user = self.get_by_email(db, email=email_or_username)
        if not user:
            # If not found by email, try by username
            user = self.get_by_username(db, username=email_or_username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

    def is_active(self, user: User) -> bool:
        """
        Check if a user is active.
        """
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """
        Check if a user is a superuser.
        """
        return user.is_superuser


crud_user = CRUDUser(User)