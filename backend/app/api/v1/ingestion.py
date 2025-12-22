from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import tempfile
from app.db.session import get_db
from app.core.dependencies import get_current_tenant
from app.schemas.knowledge import KnowledgeIngest
from app.services.ingestion_service import ingest_knowledge, ingest_file
from app.tasks.ingestion_tasks import ingest_knowledge_async
from app.db.models.knowledge_source import SourceType
import uuid

router = APIRouter()


@router.post("/ingest")
async def ingest_knowledge_endpoint(
    data: KnowledgeIngest,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    async_mode: bool = False
):
    try:
        if async_mode:
            task = ingest_knowledge_async.delay(tenant_id, data.dict())
            return {"message": "Ingestion started", "task_id": task.id, "status": "processing"}
        else:
            result = ingest_knowledge(db, tenant_id, data)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    async_mode: bool = False
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {'.pdf', '.txt', '.md'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        if async_mode:
            if tmp_file_path.endswith('.pdf'):
                from app.services.document_processor import extract_text_from_pdf
                file_content = extract_text_from_pdf(tmp_file_path)
            else:
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            
            source_id = str(uuid.uuid4())
            ingest_data = {
                "content": file_content,
                "source_type": SourceType.MANUAL_UPLOAD.value,
                "source_id": source_id,
                "version": 1,
                "name": file.filename
            }
            task = ingest_knowledge_async.delay(tenant_id, ingest_data)
            return {"message": "Upload started", "task_id": task.id, "status": "processing"}
        else:
            result = ingest_file(db, tenant_id, tmp_file_path, file.filename)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
