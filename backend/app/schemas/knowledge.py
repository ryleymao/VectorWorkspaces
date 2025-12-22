from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.db.models.knowledge_source import SourceType


class KnowledgeIngest(BaseModel):
    content: str
    source_type: SourceType
    source_id: str
    version: int = 1
    name: str


class DocumentUpload(BaseModel):
    name: str
    source_id: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    freshness_weight: float = 0.1
    exclude_deprecated: bool = True
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    retrieved_chunks: int


class ChunkResponse(BaseModel):
    id: int
    text: str
    source_id: str
    version: int
    similarity_score: float
    last_updated_at: datetime

