# app/services/user.py
from typing import Any, Dict, Optional, List, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.base import CRUDBase
from app.models.user import User
from app.dto.auth import RegisterRequest
from app.dto.user import UserCreate, UserUpdate
from app.utils.security import verify_password, get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Lấy người dùng theo email.
        
        Args:
            db: Database session
            email: Email của người dùng
            
        Returns:
            User nếu tìm thấy, None nếu không tìm thấy
        """
        query = select(self.model).where(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: Union[UserCreate, RegisterRequest]) -> User:
        """
        Tạo người dùng mới.
        
        Args:
            db: Database session
            obj_in: Dữ liệu người dùng
            
        Returns:
            Người dùng đã tạo
        """
        # Tạo user object
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_superuser=False,
            phone_number=getattr(obj_in, 'phone_number', None),
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Xác thực người dùng bằng email và mật khẩu.
        
        Args:
            db: Database session
            email: Email người dùng
            password: Mật khẩu người dùng
            
        Returns:
            Người dùng đã xác thực hoặc None
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def is_active(self, user: User) -> bool:
        """
        Kiểm tra người dùng có hoạt động không.
        
        Args:
            user: User to check
            
        Returns:
            True nếu người dùng đang hoạt động, False nếu ngược lại
        """
        return user.is_active
    
    async def is_superuser(self, user: User) -> bool:
        """
        Kiểm tra người dùng có phải là superuser không.
        
        Args:
            user: User to check
            
        Returns:
            True nếu người dùng là superuser, False nếu ngược lại
        """
        return user.is_superuser


# Tạo singleton instance
user_service = CRUDUser(User)