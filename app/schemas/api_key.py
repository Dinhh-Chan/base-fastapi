from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class APIKeyBase(BaseModel):
    name: str
    is_active: bool = True
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(APIKeyBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class APIKeyInDBBase(APIKeyBase):
    id: int
    key: str
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class APIKey(APIKeyInDBBase):
    pass


class APIKeyInDB(APIKeyInDBBase):
    pass


# app/schemas/token.py
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  
    exp: int  
    is_superuser: bool = False