# app/dto/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema cho yêu cầu đăng ký người dùng."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone_number: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema cho yêu cầu đăng nhập."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema cho phản hồi token."""
    access_token: str
    token_type: str
class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    is_superuser: bool


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[int] = None
    exp: Optional[int] = None
