"""
Simulation Service - Digital Twin
Simulates opponent responses based on learned patterns
"""
from typing import List, Dict, Optional
import random
from services.ml_service import MLService
from services.conflict_analyzer import ConflictAnalyzer

class SimulationService:
    """Digital twin simulator for opponent responses"""
    
    def __init__(self, ml_service: MLService, conflict_analyzer: ConflictAnalyzer):
        self.ml_service = ml_service
        self.conflict_analyzer = conflict_analyzer
    
    def build_opponent_model(self, opponent_turns: List[Dict]) -> Dict:
        """Build opponent personality model from their messages"""
        
        if not opponent_turns:
            return self._default_opponent_model()
        
        # Analyze linguistic patterns
        all_text = " ".join([t["text"] for t in opponent_turns])
        features = self.ml_service.extract_linguistic_features(all_text)
        
        # Sentiment baseline
        sentiments = [self.ml_service.analyze_sentiment(t["text"]) for t in opponent_turns]
        avg_sentiment = sum(s["score"] * (1 if s["label"] == "POSITIVE" else -1) for s in sentiments) / len(sentiments)
        
        # Aggression baseline
        aggression_scores = [t.get("aggression_score", 0.0) for t in opponent_turns]
        avg_aggression = sum(aggression_scores) / len(aggression_scores)
        
        # Passive aggression baseline
        passive_agg_scores = [t.get("passive_aggression_score", 0.0) for t in opponent_turns]
        avg_passive_agg = sum(passive_agg_scores) / len(passive_agg_scores)
        
        # Extract common phrases/patterns
        trigger_words = self._extract_trigger_words(opponent_turns)
        response_patterns = self._extract_response_patterns(opponent_turns)
        
        # Determine communication style
        communication_style = self._determine_communication_style(
            avg_aggression,
            avg_passive_agg,
            features
        )
        
        return {
            "linguistic_style": features,
            "sentiment_baseline": avg_sentiment,
            "aggression_baseline": avg_aggression,
            "passive_aggression_baseline": avg_passive_agg,
            "trigger_words": trigger_words,
            "response_patterns": response_patterns,
            "communication_style": communication_style
        }
    
    def simulate_response(
        self,
        user_draft: str,
        opponent_model: Dict,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        Simulate opponent's likely response to user's draft message
        """
        
        # Analyze user's draft
        draft_analysis = self.conflict_analyzer.analyze_turn(user_draft, "user")
        
        # Predict opponent reaction based on:
        # 1. User draft tone
        # 2. Opponent baseline
        # 3. Conversation trajectory
        
        response_text = self._generate_response_text(
            user_draft,
            draft_analysis,
            opponent_model
        )
        
        # Analyze simulated response
        simulated_turn = self.conflict_analyzer.analyze_turn(response_text, "opponent")
        
        # Predict escalation after this exchange
        updated_history = conversation_history + [draft_analysis, simulated_turn]
        updated_analysis = self.conflict_analyzer.analyze_conversation(updated_history)
        
        return {
            "simulated_response": response_text,
            "response_analysis": simulated_turn,
            "predicted_escalation": updated_analysis["escalation_probability"],
            "conflict_score_change": updated_analysis["overall_conflict_score"] - (
                self.conflict_analyzer.analyze_conversation(conversation_history)["overall_conflict_score"]
                if conversation_history else 0
            ),
            "recommendation": self._generate_simulation_recommendation(
                draft_analysis,
                simulated_turn,
                updated_analysis
            )
        }
    
    def _generate_response_text(
        self,
        user_draft: str,
        draft_analysis: Dict,
        opponent_model: Dict
    ) -> str:
        """
        Generate simulated opponent response
        Using rule-based + template approach (in production, could use LLM)
        """
        
        style = opponent_model.get("communication_style", "neutral")
        aggression_level = opponent_model.get("aggression_baseline", 0.3)
        
        # Check if user draft is triggering
        is_triggering = draft_analysis["conflict_score"] > 0.5
        
        # Template-based generation based on style and trigger
        templates = self._get_response_templates(style, aggression_level, is_triggering)
        
        response = random.choice(templates)
        
        # Personalize with trigger words
        trigger_words = opponent_model.get("trigger_words", [])
        if trigger_words and random.random() > 0.5:
            response += f" {random.choice(trigger_words)}"
        
        return response
    
    def _get_response_templates(
        self,
        style: str,
        aggression: float,
        is_triggering: bool
    ) -> List[str]:
        """Get response templates based on opponent profile"""
        
        templates = {
            "aggressive": {
                "calm": [
                    "That's not what I meant at all.",
                    "You're twisting my words.",
                    "Here we go again.",
                ],
                "triggered": [
                    "Are you serious right now?",
                    "You always do this!",
                    "I'm done with this conversation.",
                    "This is ridiculous.",
                ]
            },
            "passive_aggressive": {
                "calm": [
                    "Sure, whatever you say.",
                    "If that's how you feel...",
                    "I guess that's fine.",
                    "Do what you want.",
                ],
                "triggered": [
                    "Well, excuse me for existing.",
                    "Sorry for caring.",
                    "My bad for trying.",
                    "Fine. You win.",
                ]
            },
            "avoidant": {
                "calm": [
                    "Can we talk about this later?",
                    "I don't want to get into this now.",
                    "Let's just move on.",
                ],
                "triggered": [
                    "I can't deal with this right now.",
                    "I need space.",
                    "This is too much.",
                ]
            },
            "constructive": {
                "calm": [
                    "I hear what you're saying.",
                    "Let me think about that.",
                    "Can we find a middle ground?",
                ],
                "triggered": [
                    "I feel hurt by that.",
                    "This is important to me.",
                    "I need you to understand my perspective.",
                ]
            },
            "neutral": {
                "calm": [
                    "Okay.",
                    "I understand.",
                    "Let's figure this out.",
                ],
                "triggered": [
                    "I disagree with that.",
                    "That's not fair.",
                    "I don't think that's right.",
                ]
            }
        }
        
        mood = "triggered" if is_triggering else "calm"
        return templates.get(style, templates["neutral"])[mood]
    
    def _determine_communication_style(
        self,
        aggression: float,
        passive_aggression: float,
        features: Dict
    ) -> str:
        """Determine dominant communication style"""
        
        if aggression > 0.6:
            return "aggressive"
        elif passive_aggression > 0.5:
            return "passive_aggressive"
        elif features.get("you_statements", 0) > features.get("i_statements", 0) * 2:
            return "aggressive"
        elif features.get("question_count", 0) < 1 and aggression < 0.3:
            return "avoidant"
        elif aggression < 0.3 and passive_aggression < 0.3:
            return "constructive"
        else:
            return "neutral"
    
    def _extract_trigger_words(self, turns: List[Dict]) -> List[str]:
        """Extract common trigger phrases"""
        
        trigger_phrases = []
        for turn in turns:
            if turn.get("conflict_score", 0) > 0.6:
                # Extract key phrases from high-conflict turns
                text = turn["text"]
                if len(text) < 50:  # Short, punchy phrases
                    trigger_phrases.append(text)
        
        return trigger_phrases[:5]  # Top 5
    
    def _extract_response_patterns(self, turns: List[Dict]) -> List[str]:
        """Extract response patterns"""
        
        patterns = []
        for i in range(1, len(turns)):
            if turns[i]["speaker"] == "opponent":
                patterns.append({
                    "trigger": turns[i-1]["text"][:50],
                    "response": turns[i]["text"][:50]
                })
        
        return patterns[:5]
    
    def _generate_simulation_recommendation(
        self,
        draft_analysis: Dict,
        simulated_response: Dict,
        updated_analysis: Dict
    ) -> str:
        """Generate recommendation based on simulation"""
        
        escalation = updated_analysis["escalation_probability"]
        
        if escalation > 0.7:
            return "⚠️ High escalation risk. Consider rephrasing to be less confrontational."
        elif escalation > 0.5:
            return "⚡ Moderate escalation likely. Adding 'I feel' statements might help."
        else:
            return "✅ This approach seems balanced."
    
    def _default_opponent_model(self) -> Dict:
        """Return default opponent model"""
        return {
            "linguistic_style": {},
            "sentiment_baseline": 0.0,
            "aggression_baseline": 0.3,
            "passive_aggression_baseline": 0.2,
            "trigger_words": [],
            "response_patterns": [],
            "communication_style": "neutral"
        }
