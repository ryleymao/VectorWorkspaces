from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate
from typing import Optional, List


def create_user(db: Session, user_data: UserCreate, tenant_id: int) -> User:
    user = User(email=user_data.email, name=user_data.name, tenant_id=tenant_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int, tenant_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()


def get_user_by_email(db: Session, email: str, tenant_id: int) -> Optional[User]:
    return db.query(User).filter(User.email == email, User.tenant_id == tenant_id).first()


def get_users(db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).filter(User.tenant_id == tenant_id).offset(skip).limit(limit).all()

