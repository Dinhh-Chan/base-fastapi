from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.crud.user import crud_user
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, get_current_superuser
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate


router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def read_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    sort_by: Optional[str] = Query(None, description="Sắp xếp theo trường"),
    sort_order: str = Query("asc", description="Thứ tự sắp xếp (asc hoặc desc)"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    is_superuser: Optional[bool] = Query(None, description="Lọc theo quyền admin"),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy danh sách người dùng với phân trang, sắp xếp, tìm kiếm và lọc.
    """
    if search:
        # Tìm kiếm theo username, email hoặc họ tên
        result = crud_user.search(
            db, 
            search_term=search, 
            search_columns=["username", "email", "full_name"],
            page=page, 
            page_size=page_size, 
            sort_by=sort_by or "id", 
            sort_order=sort_order
        )
        return result
    
    # Xây dựng bộ lọc
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if is_superuser is not None:
        filters["is_superuser"] = is_superuser
    
    if filters:
        # Nếu có lọc
        result = crud_user.filter_by(
            db, 
            filters=filters, 
            page=page, 
            page_size=page_size, 
            sort_by=sort_by or "id", 
            sort_order=sort_order
        )
        return result
    
    # Mặc định lấy tất cả với phân trang
    result = crud_user.get_multi_paginated(
        db, 
        page=page, 
        page_size=page_size, 
        sort_by=sort_by or "id", 
        sort_order=sort_order
    )
    return result


@router.get("/all", response_model=List[UserSchema])
def read_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy tất cả người dùng không phân trang (chỉ dành cho admin).
    """
    users = crud_user.get_all(db)
    return users


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Tạo người dùng mới (chỉ admin).
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng.",
        )
    
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập này đã được sử dụng.",
        )
    
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lấy thông tin người dùng hiện tại.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    full_name: Optional[str] = Body(None),
    email: Optional[EmailStr] = Body(None),
    username: Optional[str] = Body(None),
    password: Optional[str] = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cập nhật thông tin người dùng hiện tại.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    if username is not None:
        user_in.username = username
    if password is not None:
        user_in.password = password
    
    # Kiểm tra email hoặc username đã tồn tại chưa
    if email is not None and email != current_user.email:
        user = crud_user.get_by_email(db, email=email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được sử dụng.",
            )
    
    if username is not None and username != current_user.username:
        user = crud_user.get_by_username(db, username=username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập này đã được sử dụng.",
            )
    
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Lấy thông tin người dùng theo ID.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    
    # Người dùng thường chỉ có thể xem thông tin của chính mình
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập",
        )
    
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., gt=0),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Cập nhật thông tin người dùng (chỉ admin).
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    
    # Kiểm tra email hoặc username đã tồn tại chưa
    if user_in.email is not None and user_in.email != user.email:
        user_by_email = crud_user.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được sử dụng.",
            )
    
    if user_in.username is not None and user_in.username != user.username:
        user_by_username = crud_user.get_by_username(db, username=user_in.username)
        if user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập này đã được sử dụng.",
            )
    
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Xóa người dùng (chỉ admin).
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    
    # Không cho phép xóa chính mình
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản đang sử dụng",
        )
    
    user = crud_user.remove(db, id=user_id)
    return user


@router.post("/bulk-delete", response_model=Dict[str, int])
def bulk_delete_users(
    *,
    db: Session = Depends(get_db),
    user_ids: List[int] = Body(..., embed=True),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Xóa nhiều người dùng cùng lúc (chỉ admin).
    """
    # Không cho phép xóa chính mình
    if current_user.id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản đang sử dụng",
        )
    
    deleted_count = crud_user.bulk_delete(db, ids=user_ids)
    return {"deleted_count": deleted_count}