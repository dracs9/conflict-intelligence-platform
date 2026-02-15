"""
Database Connection and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings"""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cip_user:cip_password@postgres:5432/conflict_intelligence")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    class Config:
        env_file = ".env"

settings = Settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for getting database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
