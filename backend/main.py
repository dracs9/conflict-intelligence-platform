"""
Conflict Intelligence Platform - Main Application
A production-grade conflict analysis and mediation system
"""

import json
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from api.routes import analysis, dialogue, ocr, profile, realtime, simulation
from database.connection import Base, engine, get_db
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from services.conflict_analyzer import ConflictAnalyzer
from services.ml_service import MLService

# Initialize ML models on startup
ml_service = None
conflict_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for ML models"""
    global ml_service, conflict_analyzer

    print("🚀 Initializing ML models...")
    ml_service = MLService()
    await ml_service.initialize()

    conflict_analyzer = ConflictAnalyzer(ml_service)

    # Expose services on app.state to avoid circular imports from route modules
    app.state.ml_service = ml_service
    app.state.conflict_analyzer = conflict_analyzer

    print("✅ ML models loaded successfully")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")

    yield

    print("🔄 Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Conflict Intelligence Platform",
    description="AI-powered conflict analysis and mediation system",
    version="1.0.0",
    lifespan=lifespan,
)

import logging
import os

# simple logging config (can be controlled with LOG_LEVEL env)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("cip")

# CORS configuration — read from CORS_ORIGINS (comma-separated) for dev/prod flexibility
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
if cors_origins_env.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lightweight request logger to help capture CORS / 5xx issues
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"← {request.method} {request.url} - {response.status_code}")
    return response


# Include routers
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["Dialogue"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Realtime"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Conflict Intelligence Platform",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ml_service": ml_service is not None,
        "conflict_analyzer": conflict_analyzer is not None,
        "database": "connected",
    }


@app.get("/ready")
async def readiness_probe():
    """Readiness probe — returns 503 until ML models & analyzer initialized"""
    if ml_service is None or conflict_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
