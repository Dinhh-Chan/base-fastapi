from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.crud.api_key import crud_api_key
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.api_key import APIKey, APIKeyCreate, APIKeyUpdate


router = APIRouter()


@router.get("/", response_model=List[APIKey])
def read_api_keys(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve API keys for the current user.
    """
    api_keys = crud_api_key.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return api_keys


@router.post("/", response_model=APIKey)
def create_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_in: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new API key for the current user.
    """
    api_key = crud_api_key.create_with_user(
        db=db, obj_in=api_key_in, user_id=current_user.id
    )
    return api_key


@router.post("/with-expiry", response_model=APIKey)
def create_api_key_with_expiry(
    *,
    db: Session = Depends(get_db),
    api_key_in: APIKeyCreate,
    days_valid: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new API key with expiry for the current user.
    """
    api_key = crud_api_key.create_with_expiry(
        db=db, obj_in=api_key_in, user_id=current_user.id, days_valid=days_valid
    )
    return api_key


@router.get("/{api_key_id}", response_model=APIKey)
def read_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get an API key by ID.
    """
    api_key = crud_api_key.get(db=db, id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Check if the API key belongs to the current user
    if api_key.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return api_key


@router.put("/{api_key_id}", response_model=APIKey)
def update_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_id: int = Path(..., gt=0),
    api_key_in: APIKeyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an API key.
    """
    api_key = crud_api_key.get(db=db, id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Check if the API key belongs to the current user
    if api_key.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    api_key = crud_api_key.update(db=db, db_obj=api_key, obj_in=api_key_in)
    return api_key


@router.delete("/{api_key_id}", response_model=APIKey)
def delete_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an API key.
    """
    api_key = crud_api_key.get(db=db, id=api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Check if the API key belongs to the current user
    if api_key.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    api_key = crud_api_key.remove(db=db, id=api_key_id)
    return api_key