# app/utils/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Các hằng số để export
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password context cho việc hash và verify password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác thực mật khẩu so với hash.
    
    Args:
        plain_password: Mật khẩu dạng text
        hashed_password: Mật khẩu đã hash
        
    Returns:
        True nếu mật khẩu khớp, False nếu không
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash mật khẩu.
    
    Args:
        password: Mật khẩu cần hash
        
    Returns:
        Mật khẩu đã hash
    """
    return pwd_context.hash(password)


def create_access_token(
    payload: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Tạo JWT access token.
    
    Args:
        payload: Dữ liệu đưa vào token
        expires_delta: Thời gian hết hạn tùy chọn
        
    Returns:
        JWT token đã encode
    """
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt