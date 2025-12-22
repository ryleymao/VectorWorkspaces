from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import secrets


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    invite_code = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def generate_invite_code(self):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(16)
        return self.invite_code

