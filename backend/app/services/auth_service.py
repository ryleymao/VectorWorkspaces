from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.tenant import Tenant
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings


def register_user(db: Session, user_data: UserRegister) -> dict:
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    tenant = db.query(Tenant).filter(Tenant.name == user_data.tenant_name).first()
    if not tenant:
        tenant = Tenant(name=user_data.tenant_name)
        tenant.generate_invite_code()
        db.add(tenant)
        db.flush()
    
    hashed_password = get_password_hash(user_data.password)
    from app.db.models.user import UserRole
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        tenant_id=tenant.id,
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id, "tenant_id": tenant.id})
    return {"access_token": access_token, "token_type": "bearer", "workspace_id": tenant.id}


def login_user(db: Session, user_data: UserLogin) -> dict:
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise ValueError("Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.id, "tenant_id": user.tenant_id})
    return {"access_token": access_token, "token_type": "bearer"}

