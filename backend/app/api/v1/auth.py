from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, Token
from app.services.auth_service import register_user, login_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

