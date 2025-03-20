from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import secrets
import string

from jose import jwt
from passlib.context import CryptContext

from app.core.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token, typically the user ID
        expires_delta: Optional expiration time delta from now
        
    Returns:
        JWT encoded token as a string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "is_superuser": False}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain-text password
        hashed_password: The hashed password
        
    Returns:
        Whether the password matches the hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storing.
    
    Args:
        password: The password to hash
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_api_key(key_length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        key_length: Length of the API key to generate
        
    Returns:
        A secure random API key
    """
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(key_length))
    return api_key