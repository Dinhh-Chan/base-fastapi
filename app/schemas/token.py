from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # Typically user ID
    exp: int  # Expiration time (Unix timestamp)
    is_superuser: bool = False