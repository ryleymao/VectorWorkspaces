from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.db.models.user import UserRole


class WorkspaceInvite(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class WorkspaceJoin(BaseModel):
    invite_code: str
    email: EmailStr
    name: str
    password: str


class WorkspaceMember(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceInfo(BaseModel):
    id: int
    name: str
    invite_code: Optional[str]
    member_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

