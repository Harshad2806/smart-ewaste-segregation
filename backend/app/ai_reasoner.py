"""
AI Reasoning layer for the Smart E-Waste Segregation System.

This module defines a **provider interface** (`ReasoningProvider`) so the
concrete reasoning implementation can be swapped (e.g. from deterministic
to LLM-based) without changing the API layer.

For now the only implementation is `DeterministicProvider`, a rule-based
fallback that composes structured reasoning entirely from the knowledge-base
profile — no external API or LLM is required.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# Data classes
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ReasoningInput:
    """Everything the reasoner needs to produce its output."""

    predicted_class: str
    confidence: float
    confidence_tier: str          # "high" | "medium" | "low"
    profile: dict[str, Any] | None  # full knowledge-base profile (may be None)


@dataclass(frozen=True)
class ReasoningOutput:
    """Structured AI reasoning result."""

    assessment: str
    reuse_recommendation: str
    repair_recommendation: str
    recovery_pathway: str
    recycling_recommendation: str
    risk_summary: str
    user_explanation: str


# ══════════════════════════════════════════════════════════════════════
# Provider interface
# ══════════════════════════════════════════════════════════════════════

class ReasoningProvider(ABC):
    """
    Abstract base for reasoning providers.

    To add a new provider (e.g. OpenAI, Gemini, local LLM):
      1. Subclass ``ReasoningProvider``.
      2. Implement ``reason()``.
      3. Register an instance via ``set_provider()`` at startup.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name (for logging / health checks)."""

    @abstractmethod
    def reason(self, inp: ReasoningInput) -> ReasoningOutput:
        """
        Produce a structured reasoning output given a reasoning input.

        Implementations MUST NOT invent technical or safety guidance
        that is not present in the supplied knowledge-base ``profile``.
        """


# ══════════════════════════════════════════════════════════════════════
# Deterministic (fallback) provider
# ══════════════════════════════════════════════════════════════════════

class DeterministicProvider(ReasoningProvider):
    """
    Rule-based reasoning provider that composes every output field
    directly from the knowledge-base profile.  Works offline and
    requires no external API.
    """

    @property
    def name(self) -> str:
        return "deterministic"

    def reason(self, inp: ReasoningInput) -> ReasoningOutput:
        if inp.profile is None:
            return self._unknown(inp)
        return self._from_profile(inp)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _from_profile(inp: ReasoningInput) -> ReasoningOutput:
        p = inp.profile
        assert p is not None

        category = p["category"]
        risk = p["risk_level"]
        reuse = p["reuse_potential"]
        repair = p["repairability"]
        stream = p["recycling_stream"]
        materials = p["materials"]
        safe_handling = p["safe_handling"]
        recovery_steps = p["recovery_pathway"]
        reasoning_basis = p["reasoning_basis"]

        # -- assessment ------------------------------------------------
        confidence_note = {
            "high": "The classifier identified this item with high confidence.",
            "medium": "The classifier identified this item with moderate confidence. Verify the item matches before processing.",
            "low": "The classifier identified this item with low confidence. Please verify the item type before following these recommendations.",
        }[inp.confidence_tier]

        assessment = (
            f"This item has been classified as '{inp.predicted_class}' "
            f"(category: {category}) with {inp.confidence:.0%} confidence. "
            f"{confidence_note}"
        )

        # -- reuse_recommendation --------------------------------------
        reuse_map = {
            "high": (
                f"This item has high reuse potential. Before recycling, consider "
                f"whether it can be refurbished or donated for continued use."
            ),
            "moderate": (
                f"This item has moderate reuse potential. Some components may "
                f"be reusable — consult a certified refurbisher before recycling."
            ),
            "low": (
                f"This item has low reuse potential. It is best directed to "
                f"a certified recycling facility for material recovery."
            ),
        }
        reuse_recommendation = reuse_map.get(
            reuse, "Consult a certified e-waste facility for reuse assessment."
        )

        # -- repair_recommendation -------------------------------------
        repair_map = {
            "moderate": (
                f"Repair may be feasible through authorised service centres. "
                f"Check manufacturer or certified repair programmes before disposal."
            ),
            "low": (
                f"Repair is generally not cost-effective for this item. "
                f"Proceed to certified recycling."
            ),
            "none": (
                f"This item is not repairable. Route directly to a certified "
                f"e-waste recycler for safe material recovery."
            ),
        }
        repair_recommendation = repair_map.get(
            repair,
            "Consult a certified service centre to evaluate repairability.",
        )

        # -- recovery_pathway ------------------------------------------
        recovery_pathway = (
            "Recommended recovery steps (handled by certified facility): "
            + "; ".join(recovery_steps)
            + "."
        )

        # -- recycling_recommendation ----------------------------------
        key_materials = ", ".join(materials[:3])
        recycling_recommendation = (
            f"Take this item to a '{stream}' facility. "
            f"Key recoverable materials include {key_materials}. "
            + " ".join(safe_handling[:2])
        )

        # -- risk_summary ---------------------------------------------
        risk_intro = {
            "low": "This item poses low handling risk.",
            "medium": "This item poses moderate handling risk.",
            "high": "This item poses high handling risk.",
        }[risk]
        risk_summary = risk_intro + " " + " ".join(safe_handling)

        # -- user_explanation ------------------------------------------
        user_explanation = (
            f"We identified this item as {category.lower()}. {reasoning_basis} "
            f"Please deliver it to an authorised {stream.lower()} facility "
            f"for safe and environmentally responsible processing."
        )

        return ReasoningOutput(
            assessment=assessment,
            reuse_recommendation=reuse_recommendation,
            repair_recommendation=repair_recommendation,
            recovery_pathway=recovery_pathway,
            recycling_recommendation=recycling_recommendation,
            risk_summary=risk_summary,
            user_explanation=user_explanation,
        )

    @staticmethod
    def _unknown(inp: ReasoningInput) -> ReasoningOutput:
        return ReasoningOutput(
            assessment=(
                f"The classifier predicted '{inp.predicted_class}' with "
                f"{inp.confidence:.0%} confidence, but no matching knowledge-base "
                f"profile was found."
            ),
            reuse_recommendation=(
                "Unable to assess reuse potential without a known profile. "
                "Consult a certified e-waste professional."
            ),
            repair_recommendation=(
                "Unable to assess repairability without a known profile. "
                "Consult an authorised service centre."
            ),
            recovery_pathway=(
                "Deliver the item to a certified e-waste collection point. "
                "Do not dispose of it with general household waste."
            ),
            recycling_recommendation=(
                "Take this item to the nearest certified e-waste recycling "
                "facility for safe inspection and processing."
            ),
            risk_summary=(
                "Risk level is unknown. Assume the item may contain hazardous "
                "materials and handle with care."
            ),
            user_explanation=(
                f"We could not confidently identify this item (predicted "
                f"'{inp.predicted_class}' at {inp.confidence:.0%}). "
                f"Please take it to an authorised e-waste collection centre "
                f"where professionals can inspect and process it safely."
            ),
        )


# ══════════════════════════════════════════════════════════════════════
# Module-level singleton & provider management
# ══════════════════════════════════════════════════════════════════════

_active_provider: ReasoningProvider = DeterministicProvider()


def get_provider() -> ReasoningProvider:
    """Return the currently active reasoning provider."""
    return _active_provider


def set_provider(provider: ReasoningProvider) -> None:
    """
    Replace the active reasoning provider.

    Call this at startup to switch to an LLM-backed provider, e.g.::

        from app.ai_reasoner import set_provider
        set_provider(MyOpenAIProvider(api_key=...))
    """
    global _active_provider
    logger.info("Reasoning provider changed: %s → %s", _active_provider.name, provider.name)
    _active_provider = provider


def reason(inp: ReasoningInput) -> ReasoningOutput:
    """Convenience function — delegates to the active provider."""
    return _active_provider.reason(inp)
