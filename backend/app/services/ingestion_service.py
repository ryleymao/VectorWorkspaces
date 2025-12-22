import os
import uuid
import numpy as np
from sqlalchemy.orm import Session
from app.db.models.knowledge_source import KnowledgeSource, SourceType
from app.db.models.document import Document
from app.db.models.document_chunk import DocumentChunk
from app.services.document_processor import chunk_text, extract_text_from_pdf
from app.services.embedding import embedding_service
from app.services.vector_store import VectorStore
from app.schemas.knowledge import KnowledgeIngest


def ingest_knowledge(db: Session, tenant_id: int, data: KnowledgeIngest) -> dict:
    source = db.query(KnowledgeSource).filter(
        KnowledgeSource.tenant_id == tenant_id,
        KnowledgeSource.source_id == data.source_id
    ).first()
    
    if not source:
        source = KnowledgeSource(
            tenant_id=tenant_id,
            source_type=data.source_type,
            source_id=data.source_id,
            name=data.name
        )
        db.add(source)
        db.flush()
    
    existing_doc = db.query(Document).filter(
        Document.tenant_id == tenant_id,
        Document.source_id == data.source_id,
        Document.version == data.version
    ).first()
    
    if existing_doc:
        return {"message": "Document already exists", "document_id": existing_doc.id}
    
    document = Document(
        tenant_id=tenant_id,
        knowledge_source_id=source.id,
        source_id=data.source_id,
        version=data.version
    )
    db.add(document)
    db.flush()
    
    chunks = chunk_text(data.content)
    if not chunks:
        return {"message": "No content to ingest", "document_id": document.id}
    
    vectors = embedding_service.embed_batch(chunks)
    
    vector_store = VectorStore(tenant_id)
    vector_store.load_index()
    
    chunk_ids = []
    for i, chunk_text_item in enumerate(chunks):
        chunk = DocumentChunk(
            tenant_id=tenant_id,
            document_id=document.id,
            chunk_index=i,
            chunk_text=chunk_text_item,
            source_id=data.source_id,
            version=data.version
        )
        db.add(chunk)
        db.flush()
        chunk_ids.append(chunk.id)
    
    db.commit()
    
    if len(chunk_ids) > 0:
        vector_store.add_vectors(vectors, np.array(chunk_ids))
        
        for chunk_id in chunk_ids:
            chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
            if chunk:
                chunk.faiss_id = chunk_id
        db.commit()
    
    return {"message": "Knowledge ingested", "document_id": document.id, "chunks": len(text_chunks)}


def ingest_file(db: Session, tenant_id: int, file_path: str, file_name: str) -> dict:
    source_id = str(uuid.uuid4())
    
    if file_path.endswith('.pdf'):
        content = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    ingest_data = KnowledgeIngest(
        content=content,
        source_type=SourceType.MANUAL_UPLOAD,
        source_id=source_id,
        version=1,
        name=file_name
    )
    
    return ingest_knowledge(db, tenant_id, ingest_data)
