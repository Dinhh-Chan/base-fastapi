# app/dependencies/user.py
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user import user_service
from app.dto.auth import TokenPayload
from app.core.config import settings
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Lấy người dùng hiện tại từ token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User hiện tại
        
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc người dùng không tồn tại
    """
    try:
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực thông tin đăng nhập",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Get user
    user = await user_service.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Lấy người dùng hiện tại đang hoạt động.
    
    Args:
        current_user: User hiện tại
        
    Returns:
        User hiện tại đang hoạt động
        
    Raises:
        HTTPException: Nếu người dùng không hoạt động
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )
        
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Lấy người dùng hiện tại với quyền superuser.
    
    Args:
        current_user: User hiện tại đang hoạt động
        
    Returns:
        User hiện tại với quyền superuser
        
    Raises:
        HTTPException: Nếu người dùng không có quyền superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập"
        )
        
    return current_user