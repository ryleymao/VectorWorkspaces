from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", backref="users")

