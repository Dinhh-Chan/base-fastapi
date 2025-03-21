# app/api/v1/endpoints/auth.py
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user import user_service
from app.utils.security import create_access_token
from app.dto.auth import RegisterRequest, LoginRequest, TokenResponse
from app.dto.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: RegisterRequest,
) -> Any:
    """
    Đăng ký người dùng mới.
    """
    # Kiểm tra xem email đã tồn tại chưa
    user = await user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng."
        )
    
    # Tạo user mới
    user = await user_service.create(db, obj_in=user_in)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    *,
    db: AsyncSession = Depends(get_db),
    login_in: LoginRequest,
) -> Any:
    """
    Đăng nhập và nhận access token.
    """
    user = await user_service.authenticate(
        db, email=login_in.email, password=login_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không hoạt động."
        )
    
    # Tạo và trả về token
    token = create_access_token({"user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer"
    }