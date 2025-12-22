from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Multi-Tenant Knowledge Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/knowledge_agent"
    
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "facebook/opt-1.3b"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 250
    
    FAISS_STORAGE_PATH: str = "./storage/faiss_indices"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = [".env", ".env.production", ".env.local"]
        case_sensitive = True


settings = Settings()
