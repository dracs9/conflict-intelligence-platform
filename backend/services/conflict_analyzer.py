"""
Conflict Analyzer - Core Analysis Engine
Processes dialogue and generates conflict intelligence
"""

from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from services.ml_service import MLService


class ConflictAnalyzer:
    """Main conflict analysis engine"""

    def __init__(self, ml_service: MLService):
        self.ml_service = ml_service

        # Weights for conflict score calculation
        self.weights = {
            "aggression": 0.35,
            "passive_aggression": 0.25,
            "sentiment_negativity": 0.20,
            "bias_severity": 0.20,
        }

    def analyze_turn(self, text: str, speaker: str) -> Dict:
        """Analyze a single dialogue turn"""

        # Sentiment analysis
        sentiment = self.ml_service.analyze_sentiment(text)

        # Emotion analysis
        emotions = self.ml_service.analyze_emotions(text)

        # Passive aggression detection
        passive_agg_score = self.ml_service.detect_passive_aggression(text)

        # Cognitive bias detection
        biases = self.ml_service.detect_cognitive_biases(text)

        # Linguistic features
        features = self.ml_service.extract_linguistic_features(text)

        # Calculate conflict score for this turn
        conflict_score = self._calculate_turn_conflict_score(
            aggression=emotions["aggression_score"],
            passive_aggression=passive_agg_score,
            sentiment_polarity=sentiment["polarity"],
            biases=biases,
        )

        return {
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": sentiment,
            "emotions": emotions,
            "aggression_score": emotions["aggression_score"],
            "passive_aggression_score": passive_agg_score,
            "conflict_score": conflict_score,
            "bias_tags": biases,
            "linguistic_features": features,
        }

    def _calculate_turn_conflict_score(
        self,
        aggression: float,
        passive_aggression: float,
        sentiment_polarity: float,
        biases: List[Dict],
    ) -> float:
        """Calculate conflict score for a single turn"""

        # Sentiment negativity (convert polarity to 0-1 scale)
        sentiment_negativity = (1 - sentiment_polarity) / 2

        # Bias severity score
        bias_severity_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        bias_score = 0.0
        if biases:
            bias_score = np.mean(
                [bias_severity_map.get(b.get("severity", "medium"), 0.5) for b in biases]
            )

        # Weighted sum
        conflict_score = (
            self.weights["aggression"] * aggression
            + self.weights["passive_aggression"] * passive_aggression
            + self.weights["sentiment_negativity"] * sentiment_negativity
            + self.weights["bias_severity"] * bias_score
        )

        return float(min(conflict_score, 1.0))

    def analyze_conversation(self, turns: List[Dict]) -> Dict:
        """Analyze full conversation and calculate escalation"""

        if not turns:
            return self._empty_analysis()

        # Calculate overall metrics
        conflict_scores = [t["conflict_score"] for t in turns]
        aggression_scores = [t["aggression_score"] for t in turns]
        passive_agg_scores = [t["passive_aggression_score"] for t in turns]

        overall_conflict = float(np.mean(conflict_scores))
        passive_agg_index = float(np.mean(passive_agg_scores))

        # Escalation prediction based on trend
        escalation_prob = self._predict_escalation(conflict_scores)

        # Aggregate cognitive biases
        all_biases = []
        for turn in turns:
            all_biases.extend(turn.get("bias_tags", []))

        # NVC analysis on latest turn
        nvc_analysis = self._analyze_nvc(turns[-1]["text"]) if turns else {}

        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_conflict, escalation_prob, all_biases
        )

        return {
            "overall_conflict_score": overall_conflict,
            "escalation_probability": escalation_prob,
            "passive_aggression_index": passive_agg_index,
            "cognitive_biases": all_biases,
            "nvc_analysis": nvc_analysis,
            "recommendations": recommendations,
            "trend": self._calculate_trend(conflict_scores),
            "metrics": {
                "avg_aggression": float(np.mean(aggression_scores)),
                "max_conflict": max(conflict_scores),
                "total_biases": len(all_biases),
            },
        }

    def _predict_escalation(self, conflict_scores: List[float]) -> float:
        """Predict escalation probability based on trend"""

        if len(conflict_scores) < 2:
            return float(conflict_scores[0]) if conflict_scores else 0.0

        # Calculate trend using linear regression
        x = np.arange(len(conflict_scores))
        slope = np.polyfit(x, conflict_scores, 1)[0]

        # Recent average
        recent_avg = np.mean(conflict_scores[-3:])

        # Escalation formula: recent severity + trend + volatility
        volatility = np.std(conflict_scores) if len(conflict_scores) > 2 else 0

        escalation = (
            0.4 * recent_avg
            + 0.4 * max(0, slope * 10)  # Amplify positive slopes
            + 0.2 * volatility
        )

        return float(min(escalation, 1.0))

    def _calculate_trend(self, conflict_scores: List[float]) -> str:
        """Determine conflict trend direction"""
        if len(conflict_scores) < 2:
            return "stable"

        x = np.arange(len(conflict_scores))
        slope = np.polyfit(x, conflict_scores, 1)[0]

        if slope > 0.05:
            return "escalating"
        elif slope < -0.05:
            return "de-escalating"
        else:
            return "stable"

    def _analyze_nvc(self, text: str) -> Dict:
        """
        Nonviolent Communication (NVC) analysis
        Maps message to: Observation, Evaluation, Emotion, Need
        """

        # Simplified NVC mapping
        emotions_detected = self.ml_service.analyze_emotions(text)
        dominant_emotion = emotions_detected["dominant_emotion"]

        # Map emotion to likely need
        emotion_to_need = {
            "anger": "respect, fairness, autonomy",
            "fear": "safety, security, predictability",
            "sadness": "connection, understanding, support",
            "joy": "celebration, appreciation, contribution",
            "disgust": "integrity, authenticity, order",
            "surprise": "clarity, information, understanding",
        }

        likely_need = emotion_to_need.get(dominant_emotion, "understanding, connection")

        # Check for evaluation vs observation
        has_evaluation = any(word in text.lower() for word in ["always", "never", "should", "must"])

        return {
            "observation": text,
            "has_evaluation": has_evaluation,
            "emotion": dominant_emotion,
            "likely_need": likely_need,
            "nvc_score": 0.3 if has_evaluation else 0.7,  # Higher score = more NVC-aligned
        }

    def _generate_recommendations(
        self, conflict_score: float, escalation_prob: float, biases: List[Dict]
    ) -> List[Dict]:
        """Generate actionable recommendations"""

        recommendations = []

        # High conflict
        if conflict_score > 0.7:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "de-escalation",
                    "action": "Take a break",
                    "description": "Conflict intensity is high. Consider pausing the conversation to cool down.",
                }
            )

        # Escalation risk
        if escalation_prob > 0.6:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "intervention",
                    "action": "Change communication approach",
                    "description": "Conversation is escalating. Try using 'I' statements and focus on specific behaviors.",
                }
            )

        # Cognitive biases
        if any(b.get("type") == "overgeneralization" for b in biases):
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "cognitive",
                    "action": "Avoid absolute terms",
                    "description": "Replace 'always' and 'never' with specific examples.",
                }
            )

        if any(b.get("type") == "mind_reading" for b in biases):
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "cognitive",
                    "action": "Ask instead of assume",
                    "description": "Ask about intentions rather than assuming them.",
                }
            )

        if any(b.get("type") == "gaslighting" for b in biases):
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "safety",
                    "action": "Set boundaries",
                    "description": "Gaslighting detected. Consider documenting the conversation and setting clear boundaries.",
                }
            )

        # Low conflict - positive reinforcement
        if conflict_score < 0.3:
            recommendations.append(
                {
                    "priority": "low",
                    "category": "positive",
                    "action": "Continue constructive dialogue",
                    "description": "Communication style is constructive. Keep it up!",
                }
            )

        return recommendations

    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            "overall_conflict_score": 0.0,
            "escalation_probability": 0.0,
            "passive_aggression_index": 0.0,
            "cognitive_biases": [],
            "nvc_analysis": {},
            "recommendations": [],
            "trend": "stable",
            "metrics": {},
        }
