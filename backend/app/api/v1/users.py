from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user, get_users, get_user_by_email
from app.core.dependencies import get_current_tenant
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_endpoint(
    user_data: UserCreate,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(db, user_data.email, tenant_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_data, tenant_id)


@router.get("/", response_model=List[UserResponse])
async def read_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    return get_users(db, tenant_id, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_endpoint(
    user_id: int,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id, tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
