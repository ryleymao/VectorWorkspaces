from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.ingestion_service import ingest_knowledge
from app.schemas.knowledge import KnowledgeIngest
from app.core.logger import logger


@celery_app.task(name="ingest_knowledge_async")
def ingest_knowledge_async(tenant_id: int, data: dict):
    db = SessionLocal()
    try:
        ingest_data = KnowledgeIngest(**data)
        result = ingest_knowledge(db, tenant_id, ingest_data)
        logger.info(f"Async ingestion completed for tenant {tenant_id}", extra={"document_id": result.get("document_id")})
        return result
    except Exception as e:
        logger.error(f"Async ingestion failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

