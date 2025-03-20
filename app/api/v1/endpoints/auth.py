from datetime import timedelta
from typing import Any
from app.dependencies.auth import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.core.settings import settings
from app.crud.user import crud_user
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import User, UserCreate


router = APIRouter()


@router.post("/token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Try to authenticate with username (which could be email)
    user = crud_user.get_by_email(db, email=form_data.username)
    if not user:
        # If not found by email, try by username
        user = crud_user.get_by_username(db, username=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=User)
def test_token(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Test access token.
    """
    return current_user
@router.post("/register", response_model=User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Đăng ký người dùng mới.
    """
    # Kiểm tra xem email đã tồn tại chưa
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    # Kiểm tra xem username đã tồn tại chưa
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )
    
    # Đảm bảo người dùng mới không phải là superuser
    user_data = user_in.dict()
    user_data["is_superuser"] = False
    
    # Tạo người dùng mới
    user = crud_user.create(db, obj_in=UserCreate(**user_data))
    return user
@router.post("/create-admin", status_code=201)
def create_admin(db: Session = Depends(get_db)):
    """
    Tạo tài khoản admin mới nếu chưa tồn tại.
    """
    # Kiểm tra xem admin đã tồn tại chưa
    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if user:
        return {"message": "Admin user already exists", "user_id": user.id}
    
    # Tạo admin user
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER_EMAIL,
        username=settings.FIRST_SUPERUSER_USERNAME,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
        is_active=True,
    )
    
    user = crud_user.create(db, obj_in=user_in)
    return {"message": "Admin user created successfully", "user_id": user.id}