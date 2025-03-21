# app/dto/token.py
from typing import Dict, Any, Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[Dict[str, Any]] = None
    exp: Optional[int] = None