from sqlalchemy.orm import Session
from app.db.models.tenant import Tenant
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.workspace import WorkspaceInvite
from typing import List, Optional
from fastapi import HTTPException, status


def get_workspace(db: Session, tenant_id: int) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_workspace_info(db: Session, tenant_id: int) -> dict:
    tenant = get_workspace(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    member_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "invite_code": tenant.invite_code,
        "member_count": member_count,
        "created_at": tenant.created_at
    }


def generate_invite_code(db: Session, tenant_id: int, current_user: User) -> str:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can generate invite codes")
    
    tenant = get_workspace(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    tenant.generate_invite_code()
    db.commit()
    db.refresh(tenant)
    return tenant.invite_code


def join_workspace_by_invite(db: Session, invite_code: str, email: str, name: str, password: str) -> dict:
    tenant = db.query(Tenant).filter(Tenant.invite_code == invite_code).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        name=name,
        hashed_password=hashed_password,
        tenant_id=tenant.id,
        role=UserRole.MEMBER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": user.id, "tenant_id": tenant.id})
    return {"access_token": access_token, "token_type": "bearer", "workspace_id": tenant.id}


def get_workspace_members(db: Session, tenant_id: int) -> List[User]:
    return db.query(User).filter(User.tenant_id == tenant_id).all()


def update_member_role(db: Session, tenant_id: int, user_id: int, new_role: UserRole, current_user: User) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update roles")
    
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def remove_member(db: Session, tenant_id: int, user_id: int, current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can remove members")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()

