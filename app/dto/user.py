# app/dto/user.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    email: EmailStr
    password: str
    full_name: str
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        return v


class UserUpdate(UserBase):
    """Schema for updating a user."""
    password: Optional[str] = None
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        return v


class UserStatusUpdate(BaseModel):
    """Schema for updating user status."""
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for user in DB."""
    id: int
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class UserResponse(UserInDBBase):
    """Response schema for user."""
    pass


class PaginationInfo(BaseModel):
    """Pagination info schema."""
    page: int
    page_size: int
    total: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: bool


class UserListResponse(BaseModel):
    """Response schema for user list with pagination."""
    items: List[UserResponse]
    pagination: PaginationInfo