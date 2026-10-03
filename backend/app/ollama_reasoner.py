"""
Ollama-based reasoning provider for the Smart E-Waste Segregation System.

Calls the local Ollama server (localhost:11434) to generate structured
AI reasoning from the knowledge-base profile.  Used as the primary
provider with the deterministic provider as automatic fallback.
"""

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "llama3:8b-instruct-q4_K_M"

SYSTEM_PROMPT = """\
You are an e-waste intelligence assistant for the Smart E-Waste Segregation System.

The computer-vision model has already identified the object.
You MUST NOT change, override, or reinterpret the detected class.

Use ONLY the supplied knowledge profile to inform your responses.
Do not invent materials, components, hazards, or technical facts
that are not present in the knowledge profile.

Guidelines:
- Do NOT claim a device is unrepairable unless the profile explicitly
  states repairability is "none".  When repairability is listed as
  "moderate", "low", or not specified, prefer language such as
  "consider repair or refurbishment where practical".
- Do NOT provide battery dismantling, puncturing, burning, or any
  other DIY hazardous-handling instructions.
- Do NOT invent material composition or safety hazards beyond the
  supplied knowledge profile.
- Always recommend that users take items to authorised or certified
  e-waste collection/recycling facilities.

Return ONLY valid JSON with exactly these fields:

{
  "assessment": "...",
  "reuse_recommendation": "...",
  "repair_recommendation": "...",
  "recovery_pathway": "...",
  "recycling_recommendation": "...",
  "risk_summary": "...",
  "user_explanation": "..."
}
"""

# The 7 fields expected in the Ollama JSON response.
REQUIRED_FIELDS = {
    "assessment",
    "reuse_recommendation",
    "repair_recommendation",
    "recovery_pathway",
    "recycling_recommendation",
    "risk_summary",
    "user_explanation",
}


class OllamaReasoner:
    """Async Ollama-backed reasoning provider."""

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        url: str = OLLAMA_URL,
        timeout: float = 60.0,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    async def reason(
        self,
        predicted_class: str,
        confidence: float,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call Ollama and return a validated dict with the 7 reasoning fields.

        Raises on HTTP errors, JSON parse failures, or missing fields so that
        the caller can fall back to the deterministic provider.
        """
        user_payload = {
            "detected_class": predicted_class,
            "confidence": round(confidence, 4),
            "knowledge_profile": profile,
        }

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.url, json=payload)

        response.raise_for_status()

        data = response.json()
        content = data["message"]["content"]
        result = json.loads(content)

        # Validate that all required fields are present and non-empty strings.
        missing = REQUIRED_FIELDS - set(result.keys())
        if missing:
            raise ValueError(f"Ollama response missing fields: {missing}")

        for field in REQUIRED_FIELDS:
            if not isinstance(result[field], str) or not result[field].strip():
                raise ValueError(f"Ollama field '{field}' is empty or not a string")

        logger.info("Ollama reasoning succeeded for class '%s'", predicted_class)
        return result