from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    knowledge_source_id = Column(Integer, ForeignKey("knowledge_sources.id"), nullable=False)
    source_id = Column(String, nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now())

