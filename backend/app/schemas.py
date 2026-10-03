"""
Pydantic schemas for request/response models.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str = Field(..., examples=["ok"])
    model_loaded: bool = Field(
        ..., description="Whether the classifier model is loaded and ready"
    )


# ------------------------------------------------------------------
# /predict — Vision result (classifier output)
# ------------------------------------------------------------------

class VisionResult(BaseModel):
    """Raw output from the YOLO e-waste classifier."""

    predicted_class: str = Field(
        ...,
        description="The e-waste class predicted by the classifier",
        examples=["laptops"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score between 0 and 1",
        examples=[0.92],
    )
    is_confident: bool = Field(
        ...,
        description="Whether the confidence exceeds the acceptance threshold",
    )


# ------------------------------------------------------------------
# /predict — Intelligence assessment (knowledge-base enrichment)
# ------------------------------------------------------------------

class ProfileSummary(BaseModel):
    """Material and recovery profile for the identified e-waste class."""

    category: str = Field(..., examples=["E-Waste — Computing Devices"])
    materials: list[str]
    components: list[str]
    reuse_potential: str = Field(..., examples=["high"])
    repairability: str = Field(..., examples=["moderate"])
    risk_level: str = Field(..., examples=["medium"])


class RecoveryRecommendation(BaseModel):
    """Actionable recycling and recovery guidance."""

    recycling_stream: str = Field(
        ..., examples=["Computer / Electronics Recycling"]
    )
    recovery_pathway: list[str]
    safe_handling: list[str]


class AIReasoning(BaseModel):
    """Structured AI reasoning output from the reasoning provider."""

    assessment: str = Field(
        ..., description="Overall assessment of the identified item"
    )
    reuse_recommendation: str = Field(
        ..., description="Guidance on reuse potential"
    )
    repair_recommendation: str = Field(
        ..., description="Guidance on repairability"
    )
    recovery_pathway: str = Field(
        ..., description="Summary of the recommended recovery steps"
    )
    recycling_recommendation: str = Field(
        ..., description="Specific recycling guidance for the user"
    )
    risk_summary: str = Field(
        ..., description="Summary of handling risks and safety precautions"
    )
    user_explanation: str = Field(
        ..., description="Plain-language explanation for the end user"
    )


class IntelligenceAssessment(BaseModel):
    """Structured recovery assessment from the intelligence engine."""

    class_identified: str = Field(..., examples=["laptops"])
    confidence_tier: str = Field(
        ...,
        description="Confidence bucket: high (≥0.80), medium (≥0.55), low (<0.55)",
        examples=["high"],
    )
    profile: Optional[ProfileSummary] = Field(
        None,
        description="Material profile (null when class is unknown)",
    )
    recovery_recommendation: RecoveryRecommendation
    reasoning: str = Field(
        ...,
        description="Rationale behind the recovery recommendation",
    )
    ai_reasoning: AIReasoning = Field(
        ...,
        description="Structured AI reasoning output",
    )


# ------------------------------------------------------------------
# /predict — Top-level response
# ------------------------------------------------------------------

class PredictionResponse(BaseModel):
    """Top-level wrapper for the /predict endpoint response."""

    success: bool
    vision: Optional[VisionResult] = None
    intelligence: Optional[IntelligenceAssessment] = None
    message: Optional[str] = None


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Schema for error responses."""

    success: bool = False
    detail: str
