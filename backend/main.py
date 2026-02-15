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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
