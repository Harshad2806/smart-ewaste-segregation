import asyncio

from app.ollama_reasoner import OllamaReasoner


async def main():
    reasoner = OllamaReasoner()

    profile = {
        "category": "E-Waste",
        "materials": ["glass", "plastic", "metals"],
        "components": ["PCB", "rechargeable battery"],
        "reuse_potential": "High",
        "repairability": "Medium",
        "recovery_pathway": "Reuse or authorized recycling",
        "recycling_stream": "Mobile / electronics recycling",
        "risk_level": "Medium",
        "safe_handling": [
            "Do not dismantle the battery yourself",
            "Use authorized e-waste collection"
        ]
    }

    result = await reasoner.reason(
        predicted_class="smartphones",
        confidence=0.9918,
        profile=profile,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())