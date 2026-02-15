"""
Realtime API Routes - Conflict Thermometer
"""

import json
from typing import Dict

from api.deps import get_conflict_analyzer, get_conflict_analyzer_ws
from database.connection import get_db
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from services.conflict_analyzer import ConflictAnalyzer
from sqlalchemy.orm import Session

router = APIRouter()


class RealtimeScoreRequest(BaseModel):
    text: str
    session_id: int = None


@router.post("/score")
async def realtime_score(
    request: RealtimeScoreRequest,
    conflict_analyzer: ConflictAnalyzer = Depends(get_conflict_analyzer),
):
    """
    Get real-time conflict score for text being typed
    Used for conflict thermometer
    """

    if not request.text.strip():
        return {"conflict_score": 0.0, "sentiment": "neutral", "warning_level": "safe"}

    # Quick analysis
    analysis = conflict_analyzer.analyze_turn(request.text, "user")

    # Determine warning level
    conflict_score = analysis["conflict_score"]
    if conflict_score < 0.3:
        warning_level = "safe"
        color = "green"
    elif conflict_score < 0.6:
        warning_level = "caution"
        color = "yellow"
    else:
        warning_level = "danger"
        color = "red"

    return {
        "conflict_score": conflict_score,
        "aggression_score": analysis["aggression_score"],
        "passive_aggression_score": analysis["passive_aggression_score"],
        "sentiment": analysis["sentiment"]["label"],
        "warning_level": warning_level,
        "color": color,
        "quick_tip": _get_quick_tip(conflict_score, analysis),
    }


def _get_quick_tip(conflict_score: float, analysis: Dict) -> str:
    """Generate quick tip based on analysis"""

    if conflict_score < 0.3:
        return "✅ Tone is constructive"

    biases = analysis.get("bias_tags", [])

    if any(b.get("type") == "overgeneralization" for b in biases):
        return "⚠️ Avoid 'always' and 'never'"

    if any(b.get("type") == "mind_reading" for b in biases):
        return "⚠️ Ask instead of assuming"

    if analysis["aggression_score"] > 0.6:
        return "⚠️ High aggression detected"

    if analysis["passive_aggression_score"] > 0.5:
        return "⚠️ Sounds passive-aggressive"

    return "⚡ Consider rephrasing"


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    conflict_analyzer: ConflictAnalyzer = Depends(get_conflict_analyzer_ws),
):
    """
    WebSocket endpoint for real-time conflict scoring
    """
    await manager.connect(client_id, websocket)

    try:
        while True:
            # Receive text
            data = await websocket.receive_text()
            message = json.loads(data)

            text = message.get("text", "")

            if text.strip():
                # Analyze
                analysis = conflict_analyzer.analyze_turn(text, "user")

                conflict_score = analysis["conflict_score"]

                if conflict_score < 0.3:
                    warning_level = "safe"
                    color = "green"
                elif conflict_score < 0.6:
                    warning_level = "caution"
                    color = "yellow"
                else:
                    warning_level = "danger"
                    color = "red"

                # Send response
                response = {
                    "type": "score_update",
                    "conflict_score": conflict_score,
                    "aggression_score": analysis["aggression_score"],
                    "passive_aggression_score": analysis["passive_aggression_score"],
                    "warning_level": warning_level,
                    "color": color,
                    "sentiment": analysis["sentiment"]["label"],
                    "quick_tip": _get_quick_tip(conflict_score, analysis),
                }

                await manager.send_message(client_id, response)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)
