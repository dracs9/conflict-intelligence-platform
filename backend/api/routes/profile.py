"""
Profile API Routes - User Conflict Behavior Analytics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import UserProfile, ConflictSession, DialogueTurn
import numpy as np

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get or create user conflict profile"""
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # Create new profile
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Calculate current metrics
    metrics = _calculate_user_metrics(user_id, db)
    
    # Update profile
    profile.total_conflicts = metrics["total_conflicts"]
    profile.blame_frequency = metrics["blame_frequency"]
    profile.you_statements_percentage = metrics["you_statements_percentage"]
    profile.escalation_contribution = metrics["escalation_contribution"]
    profile.dominant_style = metrics["dominant_style"]
    profile.style_distribution = metrics["style_distribution"]
    profile.conflict_history = metrics["conflict_history"]
    
    db.commit()
    
    return {
        "user_id": user_id,
        "total_conflicts": profile.total_conflicts,
        "blame_frequency": profile.blame_frequency,
        "you_statements_percentage": profile.you_statements_percentage,
        "escalation_contribution": profile.escalation_contribution,
        "dominant_style": profile.dominant_style,
        "style_distribution": profile.style_distribution,
        "conflict_history": profile.conflict_history[-10:],  # Last 10
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat()
    }

def _calculate_user_metrics(user_id: str, db: Session) -> dict:
    """Calculate user conflict behavior metrics"""
    
    # Get all user sessions
    sessions = db.query(ConflictSession).filter(
        ConflictSession.user_id == user_id
    ).all()
    
    total_conflicts = len(sessions)
    
    if total_conflicts == 0:
        return {
            "total_conflicts": 0,
            "blame_frequency": 0.0,
            "you_statements_percentage": 0.0,
            "escalation_contribution": 0.0,
            "dominant_style": "neutral",
            "style_distribution": {},
            "conflict_history": []
        }
    
    # Aggregate metrics across all sessions
    all_user_turns = []
    conflict_history = []
    
    for session in sessions:
        user_turns = db.query(DialogueTurn).filter(
            DialogueTurn.session_id == session.id,
            DialogueTurn.speaker == "user"
        ).all()
        
        all_user_turns.extend(user_turns)
        
        # Session summary
        session_conflict = np.mean([t.conflict_score for t in user_turns]) if user_turns else 0
        conflict_history.append({
            "session_id": session.id,
            "session_name": session.session_name,
            "date": session.created_at.isoformat(),
            "conflict_score": session_conflict
        })
    
    if not all_user_turns:
        return {
            "total_conflicts": total_conflicts,
            "blame_frequency": 0.0,
            "you_statements_percentage": 0.0,
            "escalation_contribution": 0.0,
            "dominant_style": "neutral",
            "style_distribution": {},
            "conflict_history": conflict_history
        }
    
    # Calculate blame frequency (biases with personalization)
    blame_count = sum(
        1 for turn in all_user_turns
        if any(b.get("type") == "personalization" for b in turn.bias_tags)
    )
    blame_frequency = blame_count / len(all_user_turns) if all_user_turns else 0
    
    # Calculate "you" statements percentage (would need linguistic features)
    # Simplified: check for "you" in text
    you_count = sum(1 for turn in all_user_turns if "you" in turn.text.lower())
    you_statements_percentage = you_count / len(all_user_turns) if all_user_turns else 0
    
    # Escalation contribution
    escalation_contribution = np.mean([t.conflict_score for t in all_user_turns])
    
    # Determine dominant style
    aggression_avg = np.mean([t.aggression_score for t in all_user_turns])
    passive_agg_avg = np.mean([t.passive_aggression_score for t in all_user_turns])
    
    if aggression_avg > 0.6:
        dominant_style = "attacking"
    elif passive_agg_avg > 0.5:
        dominant_style = "passive_aggressive"
    elif aggression_avg < 0.2 and passive_agg_avg < 0.2:
        if escalation_contribution < 0.3:
            dominant_style = "constructive"
        else:
            dominant_style = "avoidant"
    else:
        dominant_style = "neutral"
    
    # Style distribution
    style_distribution = {
        "attacking": min(aggression_avg, 1.0),
        "passive_aggressive": min(passive_agg_avg, 1.0),
        "avoidant": 0.5 if dominant_style == "avoidant" else 0.2,
        "constructive": max(0, 1.0 - escalation_contribution)
    }
    
    return {
        "total_conflicts": total_conflicts,
        "blame_frequency": blame_frequency,
        "you_statements_percentage": you_statements_percentage,
        "escalation_contribution": escalation_contribution,
        "dominant_style": dominant_style,
        "style_distribution": style_distribution,
        "conflict_history": conflict_history
    }

@router.get("/user/{user_id}/dashboard")
async def get_user_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Get comprehensive dashboard data for user"""
    
    profile_data = await get_user_profile(user_id, db)
    
    # Get recent sessions
    recent_sessions = db.query(ConflictSession).filter(
        ConflictSession.user_id == user_id
    ).order_by(ConflictSession.created_at.desc()).limit(5).all()
    
    # Calculate improvement trend
    if len(profile_data["conflict_history"]) > 1:
        recent_avg = np.mean([
            h["conflict_score"] 
            for h in profile_data["conflict_history"][-3:]
        ])
        older_avg = np.mean([
            h["conflict_score"] 
            for h in profile_data["conflict_history"][:3]
        ])
        improvement = max(0, older_avg - recent_avg) * 100
    else:
        improvement = 0
    
    return {
        "profile": profile_data,
        "recent_sessions": [
            {
                "session_id": s.id,
                "session_name": s.session_name,
                "created_at": s.created_at.isoformat(),
                "turn_count": len(s.dialogue_turns)
            }
            for s in recent_sessions
        ],
        "improvement_percentage": improvement,
        "insights": _generate_insights(profile_data)
    }

def _generate_insights(profile_data: dict) -> list:
    """Generate personalized insights"""
    
    insights = []
    
    if profile_data["blame_frequency"] > 0.5:
        insights.append({
            "type": "warning",
            "message": "High blame frequency detected. Try focusing on your own feelings and needs."
        })
    
    if profile_data["dominant_style"] == "attacking":
        insights.append({
            "type": "tip",
            "message": "Your style tends toward aggressive. Consider using 'I feel' statements."
        })
    
    if profile_data["dominant_style"] == "passive_aggressive":
        insights.append({
            "type": "tip",
            "message": "You often use passive-aggressive communication. Try being more direct."
        })
    
    if profile_data["dominant_style"] == "constructive":
        insights.append({
            "type": "positive",
            "message": "Great job! Your communication style is constructive."
        })
    
    if profile_data["escalation_contribution"] < 0.3:
        insights.append({
            "type": "positive",
            "message": "You're good at keeping conflicts from escalating."
        })
    
    return insights
