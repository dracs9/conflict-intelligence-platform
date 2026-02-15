"""Dependency helpers for app-scoped services.

Expose initialized ML and analysis services (from app.state) to route handlers
without importing `main` (prevents circular imports).
"""

from fastapi import HTTPException, Request, WebSocket
from services.simulation_service import SimulationService


def get_ml_service(request: Request):
    svc = getattr(request.app.state, "ml_service", None)
    if svc is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    return svc


def get_conflict_analyzer(request: Request):
    ca = getattr(request.app.state, "conflict_analyzer", None)
    if ca is None:
        raise HTTPException(status_code=503, detail="Conflict analyzer not initialized")
    return ca


def get_conflict_analyzer_ws(websocket: WebSocket):
    ca = getattr(websocket.app.state, "conflict_analyzer", None)
    if ca is None:
        # For WS we raise RuntimeError since HTTPException won't be sent over WS
        raise RuntimeError("Conflict analyzer not initialized")
    return ca


def get_simulation_service(request: Request):
    sim = getattr(request.app.state, "simulation_service", None)
    if sim is None:
        ml = getattr(request.app.state, "ml_service", None)
        ca = getattr(request.app.state, "conflict_analyzer", None)
        if ml is None or ca is None:
            raise HTTPException(status_code=503, detail="Services not initialized")
        sim = SimulationService(ml, ca)
        request.app.state.simulation_service = sim
    return sim
