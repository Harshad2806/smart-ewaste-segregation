"""
Tests for the intelligence engine, AI reasoner, Ollama integration,
and /predict response.

Covers:
- ewaste_profiles.json safety validation
- Intelligence engine assessments for all 5 classes (sync deterministic)
- AI reasoner (provider interface + deterministic provider) for all 5 classes
- Ollama reasoner — successful response (mocked)
- Ollama failure → deterministic fallback (mocked)
- Async assess_async round-trip
- Confidence tier boundaries
- Unknown-class fallback
- Schema round-trip (VisionResult + IntelligenceAssessment + AIReasoning)
- Decision engine threshold
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# 1. Validate ewaste_profiles.json structure and safety
# ---------------------------------------------------------------------------

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "ewaste_profiles.json"
EXPECTED_CLASSES = {"smartphones", "laptops", "electrical_cables", "electronic_chips", "small_appliances"}
REQUIRED_PROFILE_KEYS = {
    "category", "materials", "components", "reuse_potential",
    "repairability", "recovery_pathway", "recycling_stream",
    "risk_level", "safe_handling", "reasoning_basis",
}

# Phrases that indicate unsafe DIY instructions — these must NOT appear.
UNSAFE_PHRASES = [
    "strip insulation",
    "discharge capacitors",
    "extract lithium",
    "extract motherboard",
    "shred remaining",
    "wear esd-safe gloves when handling bare",
    "wear anti-static wrist strap when handling internal",
    "incinerate epoxy",
    "wear cut-resistant gloves",
    "wear gloves when handling sharp",
]

REQUIRED_AI_FIELDS = {
    "assessment", "reuse_recommendation", "repair_recommendation",
    "recovery_pathway", "recycling_recommendation", "risk_summary",
    "user_explanation",
}


def _load_profiles() -> dict:
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_profiles_json():
    """ewaste_profiles.json must exist, be valid JSON, and cover all classes."""
    assert KNOWLEDGE_PATH.exists(), f"Missing: {KNOWLEDGE_PATH}"
    profiles = _load_profiles()

    assert set(profiles.keys()) == EXPECTED_CLASSES, (
        f"Class mismatch. Expected {EXPECTED_CLASSES}, got {set(profiles.keys())}"
    )

    for cls, profile in profiles.items():
        missing = REQUIRED_PROFILE_KEYS - set(profile.keys())
        assert not missing, f"Profile '{cls}' missing keys: {missing}"
        for list_key in ("materials", "components", "recovery_pathway", "safe_handling"):
            assert isinstance(profile[list_key], list) and len(profile[list_key]) > 0, (
                f"Profile '{cls}': '{list_key}' must be a non-empty list"
            )
        for str_key in ("category", "reuse_potential", "repairability",
                        "recycling_stream", "risk_level", "reasoning_basis"):
            assert isinstance(profile[str_key], str) and len(profile[str_key]) > 0, (
                f"Profile '{cls}': '{str_key}' must be a non-empty string"
            )
    print("  PASS  test_profiles_json")


def test_profiles_no_unsafe_diy():
    """ewaste_profiles.json must not contain unsafe DIY instructions."""
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as fh:
        raw_text = fh.read().lower()

    for phrase in UNSAFE_PHRASES:
        assert phrase not in raw_text, (
            f"Unsafe DIY phrase found in profiles: '{phrase}'"
        )
    print("  PASS  test_profiles_no_unsafe_diy")


def test_profiles_point_to_certified_facilities():
    """Every profile's safe_handling must mention certified/authorised facilities."""
    profiles = _load_profiles()
    for cls, profile in profiles.items():
        handling_text = " ".join(profile["safe_handling"]).lower()
        assert "certified" in handling_text or "authorised" in handling_text or "authorized" in handling_text, (
            f"Profile '{cls}': safe_handling must reference certified/authorised facilities"
        )
    print("  PASS  test_profiles_point_to_certified_facilities")


# ---------------------------------------------------------------------------
# 2. Intelligence engine — per-class assessments (sync / deterministic)
# ---------------------------------------------------------------------------

from app.intelligence_engine import IntelligenceEngine, _confidence_tier


def _make_engine() -> IntelligenceEngine:
    engine = IntelligenceEngine()
    engine.load()
    return engine


def _assert_assessment_has_ai_reasoning(result: dict):
    """The assessment dict must include ai_reasoning with all 7 fields."""
    assert "ai_reasoning" in result, "Missing 'ai_reasoning' in assessment"
    ai = result["ai_reasoning"]
    missing = REQUIRED_AI_FIELDS - set(ai.keys())
    assert not missing, f"ai_reasoning missing fields: {missing}"
    for field in REQUIRED_AI_FIELDS:
        assert isinstance(ai[field], str) and len(ai[field]) > 0, (
            f"ai_reasoning.{field} must be a non-empty string"
        )


def test_engine_loads():
    engine = _make_engine()
    assert engine.is_loaded
    assert set(engine.known_classes) == EXPECTED_CLASSES
    print("  PASS  test_engine_loads")


def test_assess_smartphones():
    engine = _make_engine()
    result = engine.assess("smartphones", 0.91)
    assert result["class_identified"] == "smartphones"
    assert result["confidence_tier"] == "high"
    assert result["profile"]["category"] == "E-Waste — Mobile Devices"
    assert result["recovery_recommendation"]["recycling_stream"] == "Mobile / Electronics Recycling"
    assert len(result["recovery_recommendation"]["recovery_pathway"]) > 0
    assert len(result["recovery_recommendation"]["safe_handling"]) > 0
    assert isinstance(result["reasoning"], str) and len(result["reasoning"]) > 0
    _assert_assessment_has_ai_reasoning(result)
    print("  PASS  test_assess_smartphones")


def test_assess_laptops():
    engine = _make_engine()
    result = engine.assess("laptops", 0.85)
    assert result["class_identified"] == "laptops"
    assert result["confidence_tier"] == "high"
    assert result["profile"]["category"] == "E-Waste — Computing Devices"
    assert result["recovery_recommendation"]["recycling_stream"] == "Computer / Electronics Recycling"
    assert result["profile"]["reuse_potential"] == "high"
    _assert_assessment_has_ai_reasoning(result)
    print("  PASS  test_assess_laptops")


def test_assess_electrical_cables():
    engine = _make_engine()
    result = engine.assess("electrical_cables", 0.70)
    assert result["class_identified"] == "electrical_cables"
    assert result["confidence_tier"] == "medium"
    assert result["profile"]["category"] == "E-Waste — Wiring & Connectors"
    assert result["recovery_recommendation"]["recycling_stream"] == "Cable / Electronics Recycling"
    assert result["profile"]["risk_level"] == "low"
    _assert_assessment_has_ai_reasoning(result)
    print("  PASS  test_assess_electrical_cables")


def test_assess_electronic_chips():
    engine = _make_engine()
    result = engine.assess("electronic_chips", 0.60)
    assert result["class_identified"] == "electronic_chips"
    assert result["confidence_tier"] == "medium"
    assert result["profile"]["category"] == "E-Waste — Semiconductor Components"
    assert result["recovery_recommendation"]["recycling_stream"] == "Electronic Component Recycling"
    assert result["profile"]["repairability"] == "none"
    _assert_assessment_has_ai_reasoning(result)
    print("  PASS  test_assess_electronic_chips")


def test_assess_small_appliances():
    engine = _make_engine()
    result = engine.assess("small_appliances", 0.40)
    assert result["class_identified"] == "small_appliances"
    assert result["confidence_tier"] == "low"
    assert result["profile"]["category"] == "E-Waste — Small Household Appliances"
    assert result["recovery_recommendation"]["recycling_stream"] == "Small Appliance Recycling"
    assert result["profile"]["reuse_potential"] == "moderate"
    _assert_assessment_has_ai_reasoning(result)
    print("  PASS  test_assess_small_appliances")


# ---------------------------------------------------------------------------
# 3. Confidence tier boundaries
# ---------------------------------------------------------------------------

def test_confidence_tiers():
    assert _confidence_tier(0.95) == "high"
    assert _confidence_tier(0.80) == "high"
    assert _confidence_tier(0.79) == "medium"
    assert _confidence_tier(0.55) == "medium"
    assert _confidence_tier(0.54) == "low"
    assert _confidence_tier(0.00) == "low"
    print("  PASS  test_confidence_tiers")


# ---------------------------------------------------------------------------
# 4. Unknown class fallback (sync)
# ---------------------------------------------------------------------------

def test_unknown_class_fallback():
    engine = _make_engine()
    result = engine.assess("unknown_gadget", 0.30)
    assert result["class_identified"] == "unknown_gadget"
    assert result["confidence_tier"] == "low"
    assert result["profile"] is None
    assert result["recovery_recommendation"]["recycling_stream"] == "General E-Waste Recycling"
    assert "No detailed profile" in result["reasoning"]
    _assert_assessment_has_ai_reasoning(result)
    assert "unknown_gadget" in result["ai_reasoning"]["assessment"]
    print("  PASS  test_unknown_class_fallback")


# ---------------------------------------------------------------------------
# 5. AI Reasoner — provider interface and deterministic provider
# ---------------------------------------------------------------------------

from app.ai_reasoner import (
    DeterministicProvider,
    ReasoningInput,
    ReasoningOutput,
    ReasoningProvider,
    get_provider,
    set_provider,
    reason,
)


def test_provider_interface():
    """get_provider() returns a DeterministicProvider by default."""
    provider = get_provider()
    assert isinstance(provider, ReasoningProvider)
    assert isinstance(provider, DeterministicProvider)
    assert provider.name == "deterministic"
    print("  PASS  test_provider_interface")


def test_provider_is_swappable():
    """set_provider() replaces the active provider."""
    original = get_provider()

    class MockProvider(ReasoningProvider):
        @property
        def name(self) -> str:
            return "mock"
        def reason(self, inp: ReasoningInput) -> ReasoningOutput:
            return ReasoningOutput(
                assessment="mock", reuse_recommendation="mock",
                repair_recommendation="mock", recovery_pathway="mock",
                recycling_recommendation="mock", risk_summary="mock",
                user_explanation="mock",
            )

    set_provider(MockProvider())
    assert get_provider().name == "mock"
    assert reason(ReasoningInput("test", 0.5, "low", None)).assessment == "mock"

    set_provider(original)
    assert get_provider().name == "deterministic"
    print("  PASS  test_provider_is_swappable")


def test_reasoner_smartphones():
    profiles = _load_profiles()
    inp = ReasoningInput("smartphones", 0.91, "high", profiles["smartphones"])
    out = reason(inp)
    assert isinstance(out, ReasoningOutput)
    assert "smartphones" in out.assessment
    assert "reuse" in out.reuse_recommendation.lower() or "refurbish" in out.reuse_recommendation.lower()
    assert len(out.user_explanation) > 0
    print("  PASS  test_reasoner_smartphones")


def test_reasoner_laptops():
    profiles = _load_profiles()
    inp = ReasoningInput("laptops", 0.85, "high", profiles["laptops"])
    out = reason(inp)
    assert "laptops" in out.assessment
    assert "high" in out.reuse_recommendation.lower()
    assert len(out.recovery_pathway) > 0
    print("  PASS  test_reasoner_laptops")


def test_reasoner_electrical_cables():
    profiles = _load_profiles()
    inp = ReasoningInput("electrical_cables", 0.70, "medium", profiles["electrical_cables"])
    out = reason(inp)
    assert "electrical_cables" in out.assessment
    assert "low" in out.reuse_recommendation.lower()
    print("  PASS  test_reasoner_electrical_cables")


def test_reasoner_electronic_chips():
    profiles = _load_profiles()
    inp = ReasoningInput("electronic_chips", 0.60, "medium", profiles["electronic_chips"])
    out = reason(inp)
    assert "electronic_chips" in out.assessment
    assert "not repairable" in out.repair_recommendation.lower() or "not cost-effective" in out.repair_recommendation.lower()
    print("  PASS  test_reasoner_electronic_chips")


def test_reasoner_small_appliances():
    profiles = _load_profiles()
    inp = ReasoningInput("small_appliances", 0.40, "low", profiles["small_appliances"])
    out = reason(inp)
    assert "small_appliances" in out.assessment
    assert "low" in out.assessment.lower()
    assert "moderate" in out.reuse_recommendation.lower()
    print("  PASS  test_reasoner_small_appliances")


def test_reasoner_unknown_class():
    inp = ReasoningInput("alien_tech", 0.20, "low", None)
    out = reason(inp)
    assert "alien_tech" in out.assessment
    assert "certified" in out.recycling_recommendation.lower() or "authorised" in out.user_explanation.lower()
    print("  PASS  test_reasoner_unknown_class")


# ---------------------------------------------------------------------------
# 6. Ollama integration — mocked success + mocked failure
# ---------------------------------------------------------------------------

from app.ollama_reasoner import OllamaReasoner

MOCK_OLLAMA_RESPONSE = {
    "assessment": "Ollama: This smartphone was identified with high confidence.",
    "reuse_recommendation": "Ollama: Consider refurbishing this device before recycling.",
    "repair_recommendation": "Ollama: Authorised service centres can repair this device.",
    "recovery_pathway": "Ollama: Take to certified facility for battery and PCB recovery.",
    "recycling_recommendation": "Ollama: Route to Mobile / Electronics Recycling stream.",
    "risk_summary": "Ollama: Medium risk due to lithium-ion battery. Do not puncture.",
    "user_explanation": "Ollama: This smartphone contains recoverable precious metals.",
}


def test_ollama_success_mock():
    """When Ollama responds correctly, assess_async uses its output."""
    engine = _make_engine()

    mock_reason = AsyncMock(return_value=MOCK_OLLAMA_RESPONSE)

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            result = await engine.assess_async("smartphones", 0.91)
        return result

    result = asyncio.run(_run())

    assert result["class_identified"] == "smartphones"
    assert result["confidence_tier"] == "high"
    assert result["profile"] is not None
    ai = result["ai_reasoning"]
    assert ai["assessment"] == MOCK_OLLAMA_RESPONSE["assessment"]
    assert ai["reuse_recommendation"] == MOCK_OLLAMA_RESPONSE["reuse_recommendation"]
    assert ai["repair_recommendation"] == MOCK_OLLAMA_RESPONSE["repair_recommendation"]
    assert ai["recovery_pathway"] == MOCK_OLLAMA_RESPONSE["recovery_pathway"]
    assert ai["recycling_recommendation"] == MOCK_OLLAMA_RESPONSE["recycling_recommendation"]
    assert ai["risk_summary"] == MOCK_OLLAMA_RESPONSE["risk_summary"]
    assert ai["user_explanation"] == MOCK_OLLAMA_RESPONSE["user_explanation"]

    mock_reason.assert_awaited_once()
    print("  PASS  test_ollama_success_mock")


def test_ollama_failure_falls_back_to_deterministic():
    """When Ollama raises an exception, assess_async falls back to deterministic."""
    engine = _make_engine()

    mock_reason = AsyncMock(side_effect=ConnectionError("Ollama is down"))

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            result = await engine.assess_async("laptops", 0.85)
        return result

    result = asyncio.run(_run())

    assert result["class_identified"] == "laptops"
    assert result["confidence_tier"] == "high"
    assert result["profile"] is not None
    ai = result["ai_reasoning"]
    # Must have all 7 fields from deterministic fallback
    missing = REQUIRED_AI_FIELDS - set(ai.keys())
    assert not missing, f"Fallback ai_reasoning missing fields: {missing}"
    for field in REQUIRED_AI_FIELDS:
        assert isinstance(ai[field], str) and len(ai[field]) > 0
    # Must NOT contain Ollama mock content
    assert "Ollama:" not in ai["assessment"]
    # Must contain deterministic content (mentions the class)
    assert "laptops" in ai["assessment"]

    mock_reason.assert_awaited_once()
    print("  PASS  test_ollama_failure_falls_back_to_deterministic")


def test_ollama_timeout_falls_back():
    """Timeout from Ollama triggers deterministic fallback."""
    engine = _make_engine()

    import httpx
    mock_reason = AsyncMock(side_effect=httpx.TimeoutException("timed out"))

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            result = await engine.assess_async("electronic_chips", 0.60)
        return result

    result = asyncio.run(_run())

    assert result["class_identified"] == "electronic_chips"
    ai = result["ai_reasoning"]
    assert len(ai["assessment"]) > 0
    assert "Ollama:" not in ai["assessment"]
    print("  PASS  test_ollama_timeout_falls_back")


def test_ollama_invalid_json_falls_back():
    """If Ollama returns invalid JSON fields, deterministic fallback is used."""
    engine = _make_engine()

    # Return a dict missing required fields
    mock_reason = AsyncMock(side_effect=ValueError("Ollama response missing fields: {'risk_summary'}"))

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            result = await engine.assess_async("electrical_cables", 0.70)
        return result

    result = asyncio.run(_run())

    assert result["class_identified"] == "electrical_cables"
    ai = result["ai_reasoning"]
    missing = REQUIRED_AI_FIELDS - set(ai.keys())
    assert not missing
    print("  PASS  test_ollama_invalid_json_falls_back")


def test_ollama_all_five_classes_mock():
    """Ollama mock succeeds for all 5 classes via assess_async."""
    engine = _make_engine()

    mock_reason = AsyncMock(return_value=MOCK_OLLAMA_RESPONSE)

    async def _run():
        results = {}
        with patch.object(OllamaReasoner, "reason", mock_reason):
            for cls in EXPECTED_CLASSES:
                results[cls] = await engine.assess_async(cls, 0.85)
        return results

    results = asyncio.run(_run())

    for cls in EXPECTED_CLASSES:
        r = results[cls]
        assert r["class_identified"] == cls
        assert r["ai_reasoning"]["assessment"] == MOCK_OLLAMA_RESPONSE["assessment"]
    assert mock_reason.await_count == 5
    print("  PASS  test_ollama_all_five_classes_mock")


def test_ollama_unknown_class_uses_deterministic():
    """For unknown classes (no profile), assess_async always uses deterministic."""
    engine = _make_engine()

    mock_reason = AsyncMock(return_value=MOCK_OLLAMA_RESPONSE)

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            result = await engine.assess_async("mystery_device", 0.30)
        return result

    result = asyncio.run(_run())

    assert result["class_identified"] == "mystery_device"
    assert result["profile"] is None
    # Ollama should NOT be called for unknown classes (no profile to send)
    mock_reason.assert_not_awaited()
    # Deterministic fallback should have been used
    assert "mystery_device" in result["ai_reasoning"]["assessment"]
    print("  PASS  test_ollama_unknown_class_uses_deterministic")


# ---------------------------------------------------------------------------
# 7. Schema validation — full round-trip
# ---------------------------------------------------------------------------

from app.schemas import VisionResult, IntelligenceAssessment, AIReasoning, PredictionResponse


def test_schemas_round_trip():
    """Build a full PredictionResponse from assessment data and verify it serialises."""
    engine = _make_engine()
    assessment_raw = engine.assess("laptops", 0.88)

    vision = VisionResult(predicted_class="laptops", confidence=0.88, is_confident=True)
    assessment = IntelligenceAssessment(**assessment_raw)
    resp = PredictionResponse(success=True, vision=vision, intelligence=assessment)

    d = resp.model_dump()
    assert d["success"] is True
    assert d["vision"]["predicted_class"] == "laptops"
    assert d["intelligence"]["class_identified"] == "laptops"
    assert d["intelligence"]["profile"]["category"] == "E-Waste — Computing Devices"
    assert isinstance(d["intelligence"]["recovery_recommendation"]["recovery_pathway"], list)
    ai = d["intelligence"]["ai_reasoning"]
    assert isinstance(ai, dict)
    assert all(isinstance(ai[k], str) and len(ai[k]) > 0 for k in REQUIRED_AI_FIELDS)
    print("  PASS  test_schemas_round_trip")


def test_schemas_round_trip_with_ollama_mock():
    """PredictionResponse works correctly with Ollama-sourced ai_reasoning."""
    engine = _make_engine()

    mock_reason = AsyncMock(return_value=MOCK_OLLAMA_RESPONSE)

    async def _run():
        with patch.object(OllamaReasoner, "reason", mock_reason):
            return await engine.assess_async("smartphones", 0.91)

    assessment_raw = asyncio.run(_run())
    vision = VisionResult(predicted_class="smartphones", confidence=0.91, is_confident=True)
    assessment = IntelligenceAssessment(**assessment_raw)
    resp = PredictionResponse(success=True, vision=vision, intelligence=assessment)

    d = resp.model_dump()
    assert d["intelligence"]["ai_reasoning"]["assessment"] == MOCK_OLLAMA_RESPONSE["assessment"]
    print("  PASS  test_schemas_round_trip_with_ollama_mock")


# ---------------------------------------------------------------------------
# 8. Decision engine — is_confident still works
# ---------------------------------------------------------------------------

from app.decision_engine import is_confident, CONFIDENCE_THRESHOLD


def test_decision_engine_threshold():
    assert CONFIDENCE_THRESHOLD == 0.55
    assert is_confident(0.55) is True
    assert is_confident(0.56) is True
    assert is_confident(0.54) is False
    assert is_confident(0.00) is False
    print("  PASS  test_decision_engine_threshold")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # Knowledge base
    test_profiles_json,
    test_profiles_no_unsafe_diy,
    test_profiles_point_to_certified_facilities,
    # Intelligence engine (sync deterministic — all 5 classes)
    test_engine_loads,
    test_assess_smartphones,
    test_assess_laptops,
    test_assess_electrical_cables,
    test_assess_electronic_chips,
    test_assess_small_appliances,
    # Confidence tiers
    test_confidence_tiers,
    # Unknown class (sync)
    test_unknown_class_fallback,
    # AI Reasoner — provider interface
    test_provider_interface,
    test_provider_is_swappable,
    # AI Reasoner — all 5 classes + unknown (deterministic)
    test_reasoner_smartphones,
    test_reasoner_laptops,
    test_reasoner_electrical_cables,
    test_reasoner_electronic_chips,
    test_reasoner_small_appliances,
    test_reasoner_unknown_class,
    # Ollama integration (mocked)
    test_ollama_success_mock,
    test_ollama_failure_falls_back_to_deterministic,
    test_ollama_timeout_falls_back,
    test_ollama_invalid_json_falls_back,
    test_ollama_all_five_classes_mock,
    test_ollama_unknown_class_uses_deterministic,
    # Schema round-trip
    test_schemas_round_trip,
    test_schemas_round_trip_with_ollama_mock,
    # Decision engine
    test_decision_engine_threshold,
]


def main():
    print(f"\nRunning {len(ALL_TESTS)} tests...\n")
    passed = 0
    failed = 0
    for test_fn in ALL_TESTS:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {test_fn.__name__}: {exc}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(ALL_TESTS)} total")
    if failed:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
