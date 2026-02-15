"""
Simulation API Routes - Digital Twin
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import ConflictSession, DialogueTurn, OpponentModel
from services.simulation_service import SimulationService
import main

router = APIRouter()

# Initialize simulation service
simulation_service = None

@router.on_event("startup")
async def startup():
    global simulation_service
    simulation_service = SimulationService(main.ml_service, main.conflict_analyzer)

class SimulateRequest(BaseModel):
    user_draft: str

@router.post("/session/{session_id}/simulate")
async def simulate_response(
    session_id: int,
    request: SimulateRequest,
    db: Session = Depends(get_db)
):
    """
    Simulate opponent response to user's draft message
    Digital Twin in action
    """
    
    # Get conversation history
    turns = db.query(DialogueTurn).filter(
        DialogueTurn.session_id == session_id
    ).order_by(DialogueTurn.turn_id).all()
    
    # Get or build opponent model
    opponent_model_db = db.query(OpponentModel).filter(
        OpponentModel.session_id == session_id
    ).first()
    
    if not opponent_model_db:
        # Build new opponent model
        opponent_turns = [
            {
                "text": t.text,
                "speaker": t.speaker,
                "aggression_score": t.aggression_score,
                "passive_aggression_score": t.passive_aggression_score
            }
            for t in turns if t.speaker == "opponent"
        ]
        
        opponent_model = simulation_service.build_opponent_model(opponent_turns)
        
        # Save model
        opponent_model_db = OpponentModel(
            session_id=session_id,
            linguistic_style=opponent_model["linguistic_style"],
            sentiment_baseline=opponent_model["sentiment_baseline"],
            response_patterns=opponent_model["response_patterns"],
            trigger_words=opponent_model["trigger_words"],
            personality_profile={
                "communication_style": opponent_model["communication_style"],
                "aggression_baseline": opponent_model["aggression_baseline"],
                "passive_aggression_baseline": opponent_model["passive_aggression_baseline"]
            }
        )
        db.add(opponent_model_db)
        db.commit()
    else:
        # Use existing model
        opponent_model = {
            "linguistic_style": opponent_model_db.linguistic_style,
            "sentiment_baseline": opponent_model_db.sentiment_baseline,
            "aggression_baseline": opponent_model_db.personality_profile.get("aggression_baseline", 0.3),
            "passive_aggression_baseline": opponent_model_db.personality_profile.get("passive_aggression_baseline", 0.2),
            "trigger_words": opponent_model_db.trigger_words,
            "response_patterns": opponent_model_db.response_patterns,
            "communication_style": opponent_model_db.personality_profile.get("communication_style", "neutral")
        }
    
    # Convert turns to conversation history
    conversation_history = [
        {
            "speaker": t.speaker,
            "text": t.text,
            "aggression_score": t.aggression_score,
            "passive_aggression_score": t.passive_aggression_score,
            "conflict_score": t.conflict_score,
            "bias_tags": t.bias_tags
        }
        for t in turns
    ]
    
    # Run simulation
    simulation_result = simulation_service.simulate_response(
        request.user_draft,
        opponent_model,
        conversation_history
    )
    
    return {
        "user_draft": request.user_draft,
        "simulated_opponent_response": simulation_result["simulated_response"],
        "response_analysis": simulation_result["response_analysis"],
        "predicted_escalation": simulation_result["predicted_escalation"],
        "conflict_score_change": simulation_result["conflict_score_change"],
        "recommendation": simulation_result["recommendation"],
        "opponent_profile": {
            "communication_style": opponent_model["communication_style"],
            "sentiment_baseline": opponent_model["sentiment_baseline"]
        }
    }

@router.get("/session/{session_id}/opponent-profile")
async def get_opponent_profile(session_id: int, db: Session = Depends(get_db)):
    """Get opponent personality profile"""
    
    opponent_model = db.query(OpponentModel).filter(
        OpponentModel.session_id == session_id
    ).first()
    
    if not opponent_model:
        # Build on-the-fly
        turns = db.query(DialogueTurn).filter(
            DialogueTurn.session_id == session_id,
            DialogueTurn.speaker == "opponent"
        ).all()
        
        if not turns:
            raise HTTPException(status_code=404, detail="No opponent data found")
        
        opponent_turns = [
            {
                "text": t.text,
                "speaker": t.speaker,
                "aggression_score": t.aggression_score,
                "passive_aggression_score": t.passive_aggression_score
            }
            for t in turns
        ]
        
        profile = simulation_service.build_opponent_model(opponent_turns)
    else:
        profile = {
            "linguistic_style": opponent_model.linguistic_style,
            "sentiment_baseline": opponent_model.sentiment_baseline,
            "communication_style": opponent_model.personality_profile.get("communication_style"),
            "aggression_baseline": opponent_model.personality_profile.get("aggression_baseline"),
            "passive_aggression_baseline": opponent_model.personality_profile.get("passive_aggression_baseline"),
            "trigger_words": opponent_model.trigger_words
        }
    
    return {
        "session_id": session_id,
        "opponent_profile": profile
    }
