"""
ML Service - Core Intelligence Engine
Handles all ML model loading and inference
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional

import numpy as np
import spacy
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

logger = logging.getLogger(__name__)


class MLService:
    """Centralized ML service for all intelligence modules"""

    def __init__(self):
        self.sentiment_analyzer: Optional[Any] = None
        self.emotion_analyzer: Optional[Any] = None
        self.nlp: Optional[Any] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    async def initialize(self):
        """Initialize all ML models with retries and better diagnostics"""
        logger.info(f"🔧 Loading models on device: {self.device}")

        def with_retries(fn, *args, retries: int = 3, backoff: int = 2, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    wait = backoff**attempt
                    logger.warning(
                        "Model load failed (attempt %s/%s): %s — retrying in %ss",
                        attempt,
                        retries,
                        str(exc),
                        wait,
                    )
                    time.sleep(wait)
            raise RuntimeError(f"Failed to load model after {retries} attempts: {last_exc}")

        # Load sentiment analyzer (retry on transient network / HF issues)
        logger.info("Loading sentiment analyzer...")
        self.sentiment_analyzer = with_retries(
            pipeline,
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if self.device == "cuda" else -1,
            retries=3,
        )

        # Load emotion analyzer
        logger.info("Loading emotion analyzer...")
        self.emotion_analyzer = with_retries(
            pipeline,
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=0 if self.device == "cuda" else -1,
            top_k=None,
            retries=3,
        )

        # Load spaCy model (install if missing)
        logger.info("Loading spaCy...")
        for attempt in range(1, 4):
            try:
                self.nlp = spacy.load("en_core_web_sm")
                break
            except Exception as exc:
                logger.warning("spaCy model load failed (attempt %s/3): %s", attempt, exc)
                try:
                    import subprocess

                    subprocess.run(
                        [
                            "python",
                            "-m",
                            "spacy",
                            "download",
                            "en_core_web_sm",
                        ],
                        check=False,
                    )
                except Exception as e:
                    logger.warning("spaCy download attempt raised: %s", e)
                time.sleep(1 * attempt)
        if self.nlp is None:
            raise RuntimeError("Failed to load spaCy model en_core_web_sm")

        logger.info("✅ All models loaded")

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if self.sentiment_analyzer is None:
            raise RuntimeError(
                "MLService not initialized — call initialize() before using analyze_sentiment()"
            )
        results = self.sentiment_analyzer(text)
        result = results[0] if isinstance(results, list) and results else results
        if not isinstance(result, dict):
            raise RuntimeError("Unexpected response from sentiment analyzer")
        return {
            "label": result["label"],
            "score": float(result["score"]),
            "polarity": 1.0 if result["label"] == "POSITIVE" else -1.0,
        }

    def analyze_emotions(self, text: str) -> Dict:
        """Analyze emotions including aggression signals"""
        if self.emotion_analyzer is None:
            raise RuntimeError(
                "MLService not initialized — call initialize() before using analyze_emotions()"
            )
        emotions = self.emotion_analyzer(text)
        logger.debug("Raw emotion analyzer output: %s", emotions)

        if not emotions:
            return {"emotions": {}, "aggression_score": 0.0, "dominant_emotion": "neutral"}

        # Normalize different return shapes from transformers pipeline
        # Possible shapes:
        # - list[dict] -> [{"label": "anger", "score": 0.9}, ...]
        # - dict(label=..., score=...) -> single-label
        # - dict mapping labels to scores -> {"anger": 0.9, "joy": 0.1}
        emotion_dict = {}

        # Case: list of dicts with 'label' and 'score'
        if isinstance(emotions, list) and all(
            isinstance(e, dict) and "label" in e for e in emotions
        ):
            for e in emotions:
                try:
                    emotion_dict[str(e["label"])] = float(e.get("score", 0.0))
                except Exception:
                    logger.debug("Skipping malformed emotion entry: %s", e)

        # Case: single dict with 'label' and 'score'
        elif isinstance(emotions, dict) and "label" in emotions and "score" in emotions:
            emotion_dict[str(emotions["label"])] = float(emotions["score"])

        # Case: dict mapping labels -> scores
        elif isinstance(emotions, dict):
            for k, v in emotions.items():
                try:
                    emotion_dict[str(k)] = float(v)
                except Exception:
                    logger.debug("Skipping malformed emotion mapping entry: %s=%s", k, v)

        else:
            # Unknown shape — try best-effort coercion
            try:
                for item in list(emotions):
                    if isinstance(item, (tuple, list)) and len(item) == 2:
                        emotion_dict[str(item[0])] = float(item[1])
            except Exception:
                logger.exception("Unexpected emotions output type: %s", type(emotions))

        if not emotion_dict:
            # fallback
            return {"emotions": {}, "aggression_score": 0.0, "dominant_emotion": "neutral"}

        # Aggression score (anger-based)
        aggression_score = float(emotion_dict.get("anger", emotion_dict.get("Anger", 0.0)))

        # Find dominant emotion
        dominant = max(emotion_dict.items(), key=lambda kv: kv[1])[0]

        return {
            "emotions": emotion_dict,
            "aggression_score": aggression_score,
            "dominant_emotion": dominant,
        }

    def detect_passive_aggression(self, text: str) -> float:
        """
        Detect passive aggression using hybrid approach:
        - Rule-based patterns
        - Emotion analysis
        """
        score = 0.0
        text_lower = text.lower()

        # Rule-based patterns
        passive_aggressive_patterns = [
            (r"\bsure\b\.?$", 0.3),
            (r"\bwhatever\b", 0.4),
            (r"\bdo what you want\b", 0.5),
            (r"\bif you say so\b", 0.4),
            (r"\bfine\b\.?$", 0.3),
            (r"\bi guess\b", 0.2),
            (r"\bno worries\b.*\bbut\b", 0.4),
            (r"\bsorry you feel that way\b", 0.5),
            (r"\bmust be nice\b", 0.4),
            (r"\bgood for you\b", 0.3),
        ]

        for pattern, weight in passive_aggressive_patterns:
            if re.search(pattern, text_lower):
                score += weight

        # Check for sarcasm markers
        if "..." in text or "!!" in text:
            score += 0.1

        # Emotion-based detection
        emotions = self.analyze_emotions(text)

        # Passive aggression often shows as mix of negative emotions with low anger
        if emotions["aggression_score"] < 0.3 and emotions["emotions"].get("disgust", 0) > 0.3:
            score += 0.2

        # Cap at 1.0
        return min(score, 1.0)

    def detect_cognitive_biases(self, text: str) -> List[Dict]:
        """Detect cognitive biases in text"""
        biases = []
        text_lower = text.lower()

        # Overgeneralization
        overgeneralization_patterns = [
            r"\balways\b",
            r"\bnever\b",
            r"\beveryone\b",
            r"\bno one\b",
            r"\bevery time\b",
            r"\ball the time\b",
        ]
        if any(re.search(p, text_lower) for p in overgeneralization_patterns):
            biases.append(
                {
                    "type": "overgeneralization",
                    "description": "Using absolute terms (always, never, everyone)",
                    "severity": "medium",
                }
            )

        # Mind reading
        mind_reading_patterns = [
            r"\byou think\b",
            r"\byou believe\b",
            r"\byou want to\b",
            r"\byou\'re trying to\b",
            r"\byou just want\b",
        ]
        if any(re.search(p, text_lower) for p in mind_reading_patterns):
            biases.append(
                {
                    "type": "mind_reading",
                    "description": "Assuming to know other's thoughts or intentions",
                    "severity": "medium",
                }
            )

        # Catastrophizing
        catastrophizing_patterns = [
            r"\bruined\b",
            r"\bdestroyed\b",
            r"\bterrible\b",
            r"\bawful\b",
            r"\bdisaster\b",
            r"\bcatastrophe\b",
        ]
        if any(re.search(p, text_lower) for p in catastrophizing_patterns):
            biases.append(
                {
                    "type": "catastrophizing",
                    "description": "Exaggerating negative outcomes",
                    "severity": "high",
                }
            )

        # Personalization/Blame
        if re.search(r"\byou make me\b|\byou caused\b|\byour fault\b", text_lower):
            biases.append(
                {
                    "type": "personalization",
                    "description": "Attributing responsibility to others unfairly",
                    "severity": "high",
                }
            )

        # Gaslighting patterns
        gaslighting_patterns = [
            r"\byou\'re overreacting\b",
            r"\byou\'re too sensitive\b",
            r"\bthat never happened\b",
            r"\byou\'re imagining things\b",
            r"\byou\'re crazy\b",
        ]
        if any(re.search(p, text_lower) for p in gaslighting_patterns):
            biases.append(
                {
                    "type": "gaslighting",
                    "description": "Attempting to make the other doubt their perception",
                    "severity": "critical",
                }
            )

        return biases

    def extract_linguistic_features(self, text: str) -> Dict:
        """Extract linguistic features using spaCy"""
        if self.nlp is None:
            raise RuntimeError(
                "MLService not initialized — call initialize() before using extract_linguistic_features()"
            )
        doc = self.nlp(text)

        # Count "you" statements
        you_count = sum(1 for token in doc if token.text.lower() == "you")

        # Count "I" statements
        i_count = sum(1 for token in doc if token.text.lower() == "i")

        # Extract entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Question count
        question_count = text.count("?")

        return {
            "you_statements": you_count,
            "i_statements": i_count,
            "entities": entities,
            "question_count": question_count,
            "sentence_count": len(list(doc.sents)),
            "word_count": len([token for token in doc if not token.is_punct]),
        }
