from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    tenant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

