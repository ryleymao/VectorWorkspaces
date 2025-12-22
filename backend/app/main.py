from fastapi import FastAPI, Request
from time import time
from app.api.v1 import users, auth, ingestion, chat, tasks, workspace
from app.core.logger import logger
from app.utils.metrics import get_metrics, record_request, record_error

app = FastAPI(title="Multi-Tenant Knowledge Platform")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(workspace.router, prefix="/api/v1/workspace", tags=["workspace"])
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["ingestion"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time()
    
    try:
        response = await call_next(request)
        duration = time() - start_time
        
        record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        logger.info(
            "Request processed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2)
            }
        )
        
        return response
        
    except Exception as e:
        record_error(
            error_type=type(e).__name__,
            endpoint=request.url.path
        )
        
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise


@app.get("/metrics")
async def metrics():
    return get_metrics()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
