# app/api/v1/endpoints/users.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.user import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=Dict[str, Any])
async def read_user_me(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    """
    Get current user from token.
    """
    return current_user


@router.get("/protected", response_model=Dict[str, Any])
async def protected_route(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    """
    Protected route example.
    """
    return {
        "message": "This is a protected route",
        "user_data": current_user
    }