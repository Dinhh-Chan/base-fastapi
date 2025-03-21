# app/api/v1/endpoints/users.py
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.user import get_current_active_user, get_current_superuser
from app.db.session import get_db
from app.services.user import user_service
from app.models.user import User
from app.dto.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserStatusUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lấy thông tin người dùng hiện tại từ token.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cập nhật thông tin người dùng hiện tại.
    """
    updated_user = await user_service.update(db, db_obj=current_user, obj_in=user_update)
    return updated_user


@router.get("", response_model=UserListResponse)
async def get_users(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Tìm kiếm theo email hoặc tên đầy đủ"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    is_superuser: Optional[bool] = Query(None, description="Lọc theo quyền superuser"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số lượng bản ghi mỗi trang"),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy danh sách người dùng (chỉ superuser).
    """
    users = await user_service.search_users(
        db, 
        search_term=search,
        is_active=is_active,
        is_superuser=is_superuser,
        page=page,
        page_size=page_size
    )
    return users


@router.get("/status", response_model=UserListResponse)
async def get_users_by_status(
    db: AsyncSession = Depends(get_db),
    is_active: bool = Query(True, description="Trạng thái hoạt động"),
    is_superuser: bool = Query(False, description="Trạng thái superuser"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số lượng mỗi trang"),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy danh sách người dùng theo trạng thái (chỉ superuser).
    """
    users = await user_service.filter_users_by_status(
        db, 
        is_active=is_active,
        is_superuser=is_superuser,
        page=page,
        page_size=page_size
    )
    return users


@router.get("/active", response_model=List[UserResponse])
async def get_active_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng bản ghi tối đa"),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy danh sách người dùng đang hoạt động (chỉ superuser).
    """
    users = await user_service.get_active_users(db, skip=skip, limit=limit)
    return users


@router.get("/login-history", response_model=UserListResponse)
async def get_users_by_login_time(
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số lượng mỗi trang"),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy danh sách người dùng đã đăng nhập trong khoảng thời gian (chỉ superuser).
    """
    users = await user_service.get_users_by_last_login(
        db, 
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    return users


@router.get("/phone/{phone_number}", response_model=List[UserResponse])
async def get_users_by_phone(
    phone_number: str = Path(..., description="Số điện thoại tìm kiếm"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Tìm kiếm người dùng theo số điện thoại (chỉ superuser).
    """
    users = await user_service.get_users_by_phone(db, phone_number=phone_number)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int = Path(..., ge=1, description="ID của người dùng"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Lấy thông tin người dùng theo ID (chỉ superuser).
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., ge=1, description="ID của người dùng"),
    user_update: UserUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Cập nhật thông tin người dùng (chỉ superuser).
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này"
        )
    
    updated_user = await user_service.update(db, db_obj=user, obj_in=user_update)
    return updated_user


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int = Path(..., ge=1, description="ID của người dùng"),
    status_update: UserStatusUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Cập nhật trạng thái người dùng (chỉ superuser).
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này"
        )
    
    # Ngăn chặn việc vô hiệu hóa tài khoản superuser cuối cùng
    if (not status_update.is_active or status_update.is_superuser is False) and user.is_superuser:
        # Kiểm tra xem còn superuser nào khác không
        conditions = {"is_superuser": True, "is_active": True}
        superusers = await user_service.filter(db, conditions=conditions)
        if len(superusers) <= 1:  # Chỉ còn người dùng hiện tại là superuser
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể vô hiệu hóa superuser cuối cùng"
            )
    
    updated_user = await user_service.update(db, db_obj=user, obj_in=status_update)
    return updated_user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int = Path(..., ge=1, description="ID của người dùng"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Xóa người dùng (chỉ superuser).
    """
    user = await user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này"
        )
        
    # Ngăn chặn việc xóa tài khoản superuser cuối cùng
    if user.is_superuser:
        # Kiểm tra xem còn superuser nào khác không
        conditions = {"is_superuser": True, "is_active": True}
        superusers = await user_service.filter(db, conditions=conditions)
        if len(superusers) <= 1:  # Chỉ còn người dùng hiện tại là superuser
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa superuser cuối cùng"
            )
    
    deleted_user = await user_service.remove(db, id=user_id)
    return deleted_user


@router.post("/bulk-deactivate", response_model=Dict[str, Any])
async def bulk_deactivate_users(
    user_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Vô hiệu hóa nhiều người dùng cùng lúc (chỉ superuser).
    """
    # Kiểm tra xem có superuser trong danh sách không
    for user_id in user_ids:
        user = await user_service.get(db, id=user_id)
        if user and user.is_superuser:
            # Kiểm tra xem còn superuser nào khác không
            conditions = {"is_superuser": True, "is_active": True}
            superusers = await user_service.filter(db, conditions=conditions)
            if len(superusers) <= 1:  # Chỉ còn một superuser
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Không thể vô hiệu hóa superuser cuối cùng (ID: {user_id})"
                )
    
    count = await user_service.bulk_deactivate_users(db, user_ids=user_ids)
    
    return {
        "message": f"Đã vô hiệu hóa {count} người dùng",
        "deactivated_count": count
    }