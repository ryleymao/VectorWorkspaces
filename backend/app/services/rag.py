from sqlalchemy.orm import Session
from typing import List
from app.services.embedding import embedding_service
from app.services.vector_store import VectorStore
from app.db.models.document_chunk import DocumentChunk
from app.services.freshness import calculate_freshness_score
from app.services.llm import llm_service


def retrieve_chunks(
    db: Session,
    tenant_id: int,
    query: str,
    top_k: int = 5,
    freshness_weight: float = 0.1,
    exclude_deprecated: bool = True
) -> List[dict]:
    query_vector = embedding_service.embed_text(query)
    
    vector_store = VectorStore(tenant_id)
    vector_store.load_index()
    
    distances, faiss_ids = vector_store.search(query_vector, k=top_k * 2)
    
    chunks = []
    for distance, faiss_id in zip(distances, faiss_ids):
        if faiss_id == -1 or faiss_id >= len(faiss_ids):
            continue
        
        chunk = db.query(DocumentChunk).filter(
            DocumentChunk.tenant_id == tenant_id,
            DocumentChunk.id == int(faiss_id)
        ).first()
        
        if not chunk:
            continue
        
        if exclude_deprecated and chunk.is_deprecated:
            continue
        
        similarity_score = float(1.0 / (1.0 + max(distance, 0.001)))
        freshness_score = calculate_freshness_score(chunk.last_updated_at, freshness_weight)
        
        if chunk.is_deprecated:
            similarity_score *= 0.1
        
        final_score = similarity_score * freshness_score
        
        chunks.append({
            "chunk": chunk,
            "similarity_score": similarity_score,
            "freshness_score": freshness_score,
            "final_score": final_score
        })
    
    chunks.sort(key=lambda x: x["final_score"], reverse=True)
    return chunks[:top_k]


def generate_answer(query: str, chunks: List[dict]) -> str:
    context = "\n\n".join([chunk["chunk"].chunk_text for chunk in chunks])
    
    prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
    
    answer = llm_service.generate(prompt)
    return answer
