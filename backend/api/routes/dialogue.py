"""
Dialogue API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.models import ConflictSession, DialogueTurn
import main

router = APIRouter()

class CreateSessionRequest(BaseModel):
    user_id: str
    session_name: Optional[str] = None

class AddTurnRequest(BaseModel):
    speaker: str
    text: str

class TurnResponse(BaseModel):
    turn_id: int
    speaker: str
    text: str
    timestamp: str
    sentiment: dict
    aggression_score: float
    passive_aggression_score: float
    conflict_score: float
    bias_tags: List[dict]

@router.post("/session/create")
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new conflict analysis session"""
    
    session = ConflictSession(
        user_id=request.user_id,
        session_name=request.session_name or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "session_name": session.session_name,
        "created_at": session.created_at.isoformat()
    }

@router.post("/session/{session_id}/turn")
async def add_turn(
    session_id: int,
    request: AddTurnRequest,
    db: Session = Depends(get_db)
):
    """Add a dialogue turn and analyze it"""
    
    # Check session exists
    session = db.query(ConflictSession).filter(ConflictSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get turn count
    turn_count = db.query(DialogueTurn).filter(DialogueTurn.session_id == session_id).count()
    
    # Analyze turn
    analysis = main.conflict_analyzer.analyze_turn(request.text, request.speaker)
    
    # Create turn
    turn = DialogueTurn(
        session_id=session_id,
        turn_id=turn_count,
        speaker=request.speaker,
        text=request.text,
        sentiment=analysis["sentiment"]["label"],
        sentiment_score=analysis["sentiment"]["score"],
        aggression_score=analysis["aggression_score"],
        passive_aggression_score=analysis["passive_aggression_score"],
        conflict_score=analysis["conflict_score"],
        bias_tags=analysis["bias_tags"]
    )
    
    db.add(turn)
    db.commit()
    db.refresh(turn)
    
    return {
        "turn_id": turn.turn_id,
        "speaker": turn.speaker,
        "text": turn.text,
        "timestamp": turn.timestamp.isoformat(),
        "analysis": analysis
    }

@router.get("/session/{session_id}/turns")
async def get_turns(session_id: int, db: Session = Depends(get_db)):
    """Get all turns for a session"""
    
    turns = db.query(DialogueTurn).filter(
        DialogueTurn.session_id == session_id
    ).order_by(DialogueTurn.turn_id).all()
    
    return {
        "session_id": session_id,
        "turns": [
            {
                "turn_id": t.turn_id,
                "speaker": t.speaker,
                "text": t.text,
                "timestamp": t.timestamp.isoformat(),
                "sentiment": t.sentiment,
                "aggression_score": t.aggression_score,
                "passive_aggression_score": t.passive_aggression_score,
                "conflict_score": t.conflict_score,
                "bias_tags": t.bias_tags
            }
            for t in turns
        ]
    }

@router.get("/session/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get session details"""
    
    session = db.query(ConflictSession).filter(ConflictSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    turn_count = db.query(DialogueTurn).filter(DialogueTurn.session_id == session_id).count()
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_name": session.session_name,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "turn_count": turn_count
    }

@router.get("/sessions/user/{user_id}")
async def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    """Get all sessions for a user"""
    
    sessions = db.query(ConflictSession).filter(
        ConflictSession.user_id == user_id
    ).order_by(ConflictSession.created_at.desc()).all()
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": s.id,
                "session_name": s.session_name,
                "created_at": s.created_at.isoformat(),
                "turn_count": len(s.dialogue_turns)
            }
            for s in sessions
        ]
    }
