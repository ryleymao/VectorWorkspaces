from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class SourceType(str, enum.Enum):
    API = "api"
    MANUAL_UPLOAD = "manual_upload"
    DIRECTORY_INGESTION = "directory_ingestion"


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    source_type = Column(Enum(SourceType), nullable=False)
    source_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

