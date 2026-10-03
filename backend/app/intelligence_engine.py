"""
Intelligence engine for the Smart E-Waste Segregation System.

This module loads the e-waste knowledge base (ewaste_profiles.json) and
generates a structured recovery assessment for each classifier prediction.

AI reasoning flow:
  1. Try Ollama (local LLM) via OllamaReasoner.
  2. On any failure (connection refused, timeout, bad JSON, missing fields),
     fall back automatically to the deterministic provider.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.ai_reasoner import DeterministicProvider, ReasoningInput, ReasoningOutput
from app.ollama_reasoner import OllamaReasoner

logger = logging.getLogger(__name__)

# Resolve knowledge base path relative to *this* file.
# backend/app/intelligence_engine.py → backend/knowledge/
_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
_PROFILES_PATH = _KNOWLEDGE_DIR / "ewaste_profiles.json"

# Confidence thresholds for assessment tiers.
_HIGH_CONFIDENCE: float = 0.80
_MEDIUM_CONFIDENCE: float = 0.55  # matches the validated opencv_test.py threshold

# Shared instances.
_deterministic = DeterministicProvider()
_ollama = OllamaReasoner()


def _confidence_tier(confidence: float) -> str:
    """Map a raw confidence score to a human-readable tier."""
    if confidence >= _HIGH_CONFIDENCE:
        return "high"
    if confidence >= _MEDIUM_CONFIDENCE:
        return "medium"
    return "low"


def _reasoning_output_to_dict(r: ReasoningOutput) -> dict[str, str]:
    """Convert a ReasoningOutput dataclass to the ai_reasoning sub-dict."""
    return {
        "assessment": r.assessment,
        "reuse_recommendation": r.reuse_recommendation,
        "repair_recommendation": r.repair_recommendation,
        "recovery_pathway": r.recovery_pathway,
        "recycling_recommendation": r.recycling_recommendation,
        "risk_summary": r.risk_summary,
        "user_explanation": r.user_explanation,
    }


class IntelligenceEngine:
    """
    Intelligence layer that enriches classifier predictions with
    material-recovery knowledge and AI reasoning.

    Primary: Ollama (local LLM).
    Fallback: deterministic rule-based provider.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load the e-waste profiles JSON (call once at startup)."""
        if not _PROFILES_PATH.exists():
            raise FileNotFoundError(
                f"E-waste profiles not found at {_PROFILES_PATH}"
            )
        with open(_PROFILES_PATH, "r", encoding="utf-8") as fh:
            self._profiles = json.load(fh)
        logger.info(
            "Intelligence engine loaded %d e-waste profiles from %s",
            len(self._profiles),
            _PROFILES_PATH,
        )

    @property
    def is_loaded(self) -> bool:
        return len(self._profiles) > 0

    @property
    def known_classes(self) -> list[str]:
        return list(self._profiles.keys())

    def get_profile(self, class_name: str) -> dict[str, Any] | None:
        """Return the raw profile dict for a class, or None."""
        return self._profiles.get(class_name)

    # ------------------------------------------------------------------
    # Synchronous assess (deterministic only — used by tests)
    # ------------------------------------------------------------------

    def assess(self, predicted_class: str, confidence: float) -> dict[str, Any]:
        """
        Generate a structured recovery assessment (synchronous).

        Uses only the deterministic provider — no Ollama call.
        Kept for backwards-compatible test usage.
        """
        tier = _confidence_tier(confidence)
        profile = self._profiles.get(predicted_class)

        ai_reasoning = _reasoning_output_to_dict(
            _deterministic.reason(ReasoningInput(
                predicted_class=predicted_class,
                confidence=confidence,
                confidence_tier=tier,
                profile=profile,
            ))
        )

        if profile is None:
            return self._build_unknown(predicted_class, tier, ai_reasoning)

        return self._build_known(predicted_class, profile, tier, ai_reasoning)

    # ------------------------------------------------------------------
    # Async assess (Ollama → deterministic fallback)
    # ------------------------------------------------------------------

    async def assess_async(
        self, predicted_class: str, confidence: float
    ) -> dict[str, Any]:
        """
        Generate a structured recovery assessment (async).

        Tries Ollama first; on any failure falls back to deterministic.
        """
        tier = _confidence_tier(confidence)
        profile = self._profiles.get(predicted_class)

        ai_reasoning = await self._get_ai_reasoning(
            predicted_class, confidence, tier, profile,
        )

        if profile is None:
            return self._build_unknown(predicted_class, tier, ai_reasoning)

        return self._build_known(predicted_class, profile, tier, ai_reasoning)

    # ------------------------------------------------------------------
    # AI Reasoning — Ollama first, deterministic fallback
    # ------------------------------------------------------------------

    async def _get_ai_reasoning(
        self,
        predicted_class: str,
        confidence: float,
        tier: str,
        profile: dict[str, Any] | None,
    ) -> dict[str, str]:
        """Try Ollama; on any error, use deterministic provider."""
        if profile is not None:
            try:
                ollama_result = await _ollama.reason(
                    predicted_class=predicted_class,
                    confidence=confidence,
                    profile=profile,
                )
                logger.info(
                    "AI reasoning via Ollama for class '%s'", predicted_class,
                )
                return ollama_result
            except Exception as exc:
                logger.warning(
                    "Ollama failed for class '%s': %s — using deterministic fallback",
                    predicted_class,
                    exc,
                )

        # Deterministic fallback (always works, no network needed).
        return _reasoning_output_to_dict(
            _deterministic.reason(ReasoningInput(
                predicted_class=predicted_class,
                confidence=confidence,
                confidence_tier=tier,
                profile=profile,
            ))
        )

    # ------------------------------------------------------------------
    # Response builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_known(
        predicted_class: str,
        profile: dict[str, Any],
        tier: str,
        ai_reasoning: dict[str, str],
    ) -> dict[str, Any]:
        return {
            "class_identified": predicted_class,
            "confidence_tier": tier,
            "profile": {
                "category": profile["category"],
                "materials": profile["materials"],
                "components": profile["components"],
                "reuse_potential": profile["reuse_potential"],
                "repairability": profile["repairability"],
                "risk_level": profile["risk_level"],
            },
            "recovery_recommendation": {
                "recycling_stream": profile["recycling_stream"],
                "recovery_pathway": profile["recovery_pathway"],
                "safe_handling": profile["safe_handling"],
            },
            "reasoning": profile["reasoning_basis"],
            "ai_reasoning": ai_reasoning,
        }

    @staticmethod
    def _build_unknown(
        predicted_class: str,
        tier: str,
        ai_reasoning: dict[str, str],
    ) -> dict[str, Any]:
        return {
            "class_identified": predicted_class,
            "confidence_tier": tier,
            "profile": None,
            "recovery_recommendation": {
                "recycling_stream": "General E-Waste Recycling",
                "recovery_pathway": [
                    "Deliver to a certified e-waste collection point",
                    "Do not dispose with general household waste",
                ],
                "safe_handling": [
                    "Assume the item may contain hazardous materials",
                    "Use only authorised e-waste recycling facilities for disposal",
                ],
            },
            "reasoning": (
                f"No detailed profile available for class '{predicted_class}'. "
                "Defaulting to safe general e-waste disposal."
            ),
            "ai_reasoning": ai_reasoning,
        }


# Module-level singleton — loaded once at startup via lifespan.
intelligence = IntelligenceEngine()
