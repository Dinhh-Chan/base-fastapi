import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, validator, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Cấu hình để chấp nhận các trường dư thừa
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # Cho phép các biến không được định nghĩa trong model
    )
    
    PROJECT_NAME: str = "FastAPI Application"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0
    ALGORITHM: str = "HS256"
    
    # BACKEND_CORS_ORIGINS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # DATABASE
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"
    
    # USERS
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    
    # LOGGING
    LOG_LEVEL: str = "INFO"


settings = Settings()