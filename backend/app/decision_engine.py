"""
Decision engine — confidence thresholds for the classifier.

Recycling streams, recommendations, and material profiles are now handled
by the intelligence engine (intelligence_engine.py) backed by the
knowledge base (knowledge/ewaste_profiles.json).

This module retains only the confidence-threshold logic used as a
lightweight gate before the full intelligence assessment.
"""

# Confidence threshold aligned with the validated opencv_test.py prototype.
CONFIDENCE_THRESHOLD: float = 0.55


def is_confident(confidence: float) -> bool:
    """Return True if the confidence meets the acceptance threshold."""
    return confidence >= CONFIDENCE_THRESHOLD
