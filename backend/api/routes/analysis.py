"""
Analysis API Routes
"""

from typing import List

from api.deps import get_conflict_analyzer
from database.connection import get_db
from database.models import ConflictAnalysis, ConflictSession, DialogueTurn
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.conflict_analyzer import ConflictAnalyzer
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/session/{session_id}/analyze")
async def analyze_session(
    session_id: int,
    db: Session = Depends(get_db),
    conflict_analyzer: ConflictAnalyzer = Depends(get_conflict_analyzer),
):
    """Perform complete conflict analysis on a session"""

    # Get session and turns
    session = db.query(ConflictSession).filter(ConflictSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    turns = (
        db.query(DialogueTurn)
        .filter(DialogueTurn.session_id == session_id)
        .order_by(DialogueTurn.turn_id)
        .all()
    )

    if not turns:
        raise HTTPException(status_code=400, detail="No dialogue turns found")

    # Convert to analysis format
    turn_data = [
        {
            "speaker": t.speaker,
            "text": t.text,
            "aggression_score": t.aggression_score,
            "passive_aggression_score": t.passive_aggression_score,
            "conflict_score": t.conflict_score,
            "bias_tags": t.bias_tags,
        }
        for t in turns
    ]

    # Perform analysis
    analysis_result = conflict_analyzer.analyze_conversation(turn_data)

    # Save analysis
    analysis = ConflictAnalysis(
        session_id=session_id,
        overall_conflict_score=analysis_result["overall_conflict_score"],
        escalation_probability=analysis_result["escalation_probability"],
        passive_aggression_index=analysis_result["passive_aggression_index"],
        nvc_analysis=analysis_result["nvc_analysis"],
        cognitive_biases=analysis_result["cognitive_biases"],
        recommendations=analysis_result["recommendations"],
        pipeline_data=analysis_result,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "session_id": session_id,
        "overall_conflict_score": analysis.overall_conflict_score,
        "escalation_probability": analysis.escalation_probability,
        "passive_aggression_index": analysis.passive_aggression_index,
        "trend": analysis_result["trend"],
        "cognitive_biases": analysis.cognitive_biases,
        "nvc_analysis": analysis.nvc_analysis,
        "recommendations": analysis.recommendations,
        "metrics": analysis_result.get("metrics", {}),
        "created_at": analysis.created_at.isoformat(),
    }


@router.get("/session/{session_id}/analysis/latest")
async def get_latest_analysis(session_id: int, db: Session = Depends(get_db)):
    """Get the latest analysis for a session"""

    analysis = (
        db.query(ConflictAnalysis)
        .filter(ConflictAnalysis.session_id == session_id)
        .order_by(ConflictAnalysis.created_at.desc())
        .first()
    )

    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")

    return {
        "analysis_id": analysis.id,
        "session_id": session_id,
        "overall_conflict_score": analysis.overall_conflict_score,
        "escalation_probability": analysis.escalation_probability,
        "passive_aggression_index": analysis.passive_aggression_index,
        "cognitive_biases": analysis.cognitive_biases,
        "nvc_analysis": analysis.nvc_analysis,
        "recommendations": analysis.recommendations,
        "pipeline_data": analysis.pipeline_data,
        "created_at": analysis.created_at.isoformat(),
    }


@router.get("/session/{session_id}/pipeline")
async def get_analysis_pipeline(session_id: int, db: Session = Depends(get_db)):
    """
    Get full analysis pipeline visualization data
    Shows: Input → Emotion → Bias → Need → Risk → Recommendations
    """

    # Get turns
    turns = (
        db.query(DialogueTurn)
        .filter(DialogueTurn.session_id == session_id)
        .order_by(DialogueTurn.turn_id)
        .all()
    )

    if not turns:
        raise HTTPException(status_code=404, detail="No turns found")

    # Get latest analysis
    analysis = (
        db.query(ConflictAnalysis)
        .filter(ConflictAnalysis.session_id == session_id)
        .order_by(ConflictAnalysis.created_at.desc())
        .first()
    )

    # Build pipeline visualization
    pipeline_steps = []

    for turn in turns:
        step = {
            "turn_id": turn.turn_id,
            "speaker": turn.speaker,
            "stages": [
                {"stage": "input", "label": "Said", "content": turn.text},
                {
                    "stage": "emotion",
                    "label": "Detected Emotion",
                    "content": {
                        "sentiment": turn.sentiment,
                        "aggression": turn.aggression_score,
                        "passive_aggression": turn.passive_aggression_score,
                    },
                },
                {"stage": "bias", "label": "Cognitive Biases", "content": turn.bias_tags},
                {
                    "stage": "nvc",
                    "label": "Hidden Need",
                    "content": analysis.nvc_analysis if analysis else {},
                },
                {
                    "stage": "risk",
                    "label": "Escalation Risk",
                    "content": {
                        "conflict_score": turn.conflict_score,
                        "overall_escalation": analysis.escalation_probability if analysis else 0,
                    },
                },
            ],
        }
        pipeline_steps.append(step)

    return {
        "session_id": session_id,
        "pipeline": pipeline_steps,
        "recommendations": analysis.recommendations if analysis else [],
    }
