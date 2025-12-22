from fastapi import APIRouter, HTTPException
from app.tasks.celery_app import celery_app

router = APIRouter()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {"status": "pending"}
    elif task.state == "PROCESSING":
        response = {"status": "processing", "progress": task.info.get("progress", 0)}
    elif task.state == "SUCCESS":
        response = {"status": "completed", "result": task.result}
    else:
        response = {"status": "failed", "error": str(task.info)}
    
    return response

