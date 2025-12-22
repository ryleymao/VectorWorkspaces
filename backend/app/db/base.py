from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

Base = declarative_base()

