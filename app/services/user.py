# app/services/user.py
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

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
            
        # Cập nhật thời gian đăng nhập cuối cùng
        user.last_login = datetime.now()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
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
    
    async def get_active_users(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lấy danh sách người dùng đang hoạt động.
        
        Args:
            db: Database session
            skip: Số lượng bản ghi bỏ qua
            limit: Số lượng bản ghi tối đa trả về
            
        Returns:
            Danh sách người dùng đang hoạt động
        """
        conditions = {"is_active": True}
        return await self.filter(db, conditions=conditions, skip=skip, limit=limit)
    
    async def filter_users_by_status(
        self, 
        db: AsyncSession, 
        *, 
        is_active: bool = True,
        is_superuser: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Lấy danh sách người dùng theo trạng thái với phân trang.
        
        Args:
            db: Database session
            is_active: Trạng thái hoạt động của người dùng
            is_superuser: Trạng thái superuser của người dùng
            page: Số trang
            page_size: Số lượng bản ghi mỗi trang
            
        Returns:
            Dict chứa danh sách người dùng và thông tin phân trang
        """
        exact_filters = {
            "is_active": is_active,
            "is_superuser": is_superuser
        }
        
        return await self.get_multi_paginated(
            db,
            page=page,
            page_size=page_size,
            exact_fields=exact_filters,
            order_by="full_name"
        )
    
    async def search_users(
        self, 
        db: AsyncSession, 
        *, 
        search_term: str = None,
        is_active: bool = None,
        is_superuser: bool = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Tìm kiếm người dùng với các điều kiện lọc và phân trang.
        
        Args:
            db: Database session
            search_term: Từ khóa tìm kiếm (tìm trong email và full_name)
            is_active: Lọc theo trạng thái hoạt động
            is_superuser: Lọc theo quyền superuser
            page: Số trang
            page_size: Số lượng bản ghi mỗi trang
            
        Returns:
            Dict chứa danh sách người dùng và thông tin phân trang
        """
        search_fields = {}
        exact_fields = {}
        
        if search_term:
            search_fields = {
                "email": search_term,
                "full_name": search_term
            }
            
        if is_active is not None:
            exact_fields["is_active"] = is_active
            
        if is_superuser is not None:
            exact_fields["is_superuser"] = is_superuser
            
        return await self.get_multi_paginated(
            db,
            page=page,
            page_size=page_size,
            search_fields=search_fields,
            exact_fields=exact_fields,
            order_by="full_name"
        )
    
    async def get_users_by_last_login(
        self, 
        db: AsyncSession, 
        *, 
        start_date: str, 
        end_date: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Lấy danh sách người dùng đăng nhập trong khoảng thời gian.
        
        Args:
            db: Database session
            start_date: Ngày bắt đầu (định dạng YYYY-MM-DD)
            end_date: Ngày kết thúc (định dạng YYYY-MM-DD)
            page: Số trang
            page_size: Số lượng bản ghi mỗi trang
            
        Returns:
            Dict chứa danh sách người dùng và thông tin phân trang
        """
        date_range = {
            "last_login": (start_date, end_date)
        }
        
        return await self.get_multi_paginated(
            db,
            page=page,
            page_size=page_size,
            date_range=date_range,
            order_by="last_login",
            order_direction="desc"
        )
    
    async def bulk_deactivate_users(
        self, 
        db: AsyncSession, 
        *, 
        user_ids: List[int]
    ) -> int:
        """
        Vô hiệu hóa nhiều người dùng cùng lúc.
        
        Args:
            db: Database session
            user_ids: Danh sách ID người dùng cần vô hiệu hóa
            
        Returns:
            Số lượng người dùng đã vô hiệu hóa
        """
        update_data = {"is_active": False}
        return await self.bulk_update(db, ids=user_ids, obj_in=update_data)
        
    async def get_users_by_phone(
        self,
        db: AsyncSession,
        *,
        phone_number: str
    ) -> List[User]:
        """
        Tìm kiếm người dùng theo số điện thoại.
        
        Args:
            db: Database session
            phone_number: Số điện thoại cần tìm
            
        Returns:
            Danh sách người dùng có số điện thoại phù hợp
        """
        search_fields = {"phone_number": phone_number}
        result = await self.get_multi_paginated(
            db,
            page=1,
            page_size=100,
            search_fields=search_fields
        )
        return result["items"]


# Tạo singleton instance
user_service = CRUDUser(User)