"""
Database Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class ConflictSession(Base):
    """Main conflict analysis session"""
    __tablename__ = "conflict_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dialogue_turns = relationship("DialogueTurn", back_populates="session", cascade="all, delete-orphan")
    analyses = relationship("ConflictAnalysis", back_populates="session", cascade="all, delete-orphan")

class DialogueTurn(Base):
    """Individual dialogue turn in a conversation"""
    __tablename__ = "dialogue_turns"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conflict_sessions.id"), nullable=False)
    turn_id = Column(Integer, nullable=False)
    speaker = Column(String, nullable=False)  # 'user' or 'opponent'
    timestamp = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=False)
    
    # ML Analysis results
    sentiment = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    aggression_score = Column(Float, default=0.0)
    passive_aggression_score = Column(Float, default=0.0)
    conflict_score = Column(Float, default=0.0)
    bias_tags = Column(JSON, default=list)
    
    # Relationships
    session = relationship("ConflictSession", back_populates="dialogue_turns")

class ConflictAnalysis(Base):
    """Complete analysis of a conflict session"""
    __tablename__ = "conflict_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conflict_sessions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Overall metrics
    overall_conflict_score = Column(Float, nullable=False)
    escalation_probability = Column(Float, nullable=False)
    passive_aggression_index = Column(Float, nullable=False)
    
    # NVC Analysis
    nvc_analysis = Column(JSON, nullable=True)
    
    # Cognitive biases detected
    cognitive_biases = Column(JSON, default=list)
    
    # Recommendations
    recommendations = Column(JSON, default=list)
    
    # Full analysis pipeline
    pipeline_data = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ConflictSession", back_populates="analyses")

class UserProfile(Base):
    """User conflict behavior profile"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Behavioral metrics
    total_conflicts = Column(Integer, default=0)
    blame_frequency = Column(Float, default=0.0)
    you_statements_percentage = Column(Float, default=0.0)
    escalation_contribution = Column(Float, default=0.0)
    
    # Dominant style
    dominant_style = Column(String, default="neutral")  # attacking, avoidant, passive_aggressive, constructive
    
    # Historical data
    conflict_history = Column(JSON, default=list)
    style_distribution = Column(JSON, default=dict)

class OpponentModel(Base):
    """Digital twin model of conversation opponent"""
    __tablename__ = "opponent_models"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conflict_sessions.id"), nullable=False)
    
    # Linguistic profile
    linguistic_style = Column(JSON, nullable=True)
    sentiment_baseline = Column(Float, default=0.0)
    
    # Response patterns
    response_patterns = Column(JSON, default=list)
    trigger_words = Column(JSON, default=list)
    
    # Personality traits
    personality_profile = Column(JSON, nullable=True)
