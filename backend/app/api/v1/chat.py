from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_tenant
from app.schemas.knowledge import QueryRequest, QueryResponse
from app.services.rag import retrieve_chunks, generate_answer

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_knowledge(
    query_data: QueryRequest,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    chunks_data = retrieve_chunks(
        db=db,
        tenant_id=tenant_id,
        query=query_data.query,
        top_k=query_data.top_k,
        freshness_weight=query_data.freshness_weight,
        exclude_deprecated=query_data.exclude_deprecated
    )
    
    if not chunks_data:
        return QueryResponse(
            answer="No relevant information found in the knowledge base.",
            sources=[],
            retrieved_chunks=0
        )
    
    answer = generate_answer(query_data.query, chunks_data)
    
    sources = [
        {
            "source_id": chunk["chunk"].source_id,
            "version": chunk["chunk"].version,
            "similarity_score": float(chunk["similarity_score"]),
            "last_updated_at": chunk["chunk"].last_updated_at.isoformat() if chunk["chunk"].last_updated_at else None
        }
        for chunk in chunks_data
    ]
    
    return QueryResponse(
        answer=answer,
        sources=sources,
        retrieved_chunks=len(chunks_data)
    )
