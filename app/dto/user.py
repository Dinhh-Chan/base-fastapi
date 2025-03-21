# app/dto/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr


# Các thuộc tính chung
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True


# Thuộc tính để nhận qua API khi tạo
class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str


# Thuộc tính để nhận qua API khi cập nhật
class UserUpdate(UserBase):
    password: Optional[str] = None


# Thuộc tính để trả về qua API
class UserResponse(UserBase):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True