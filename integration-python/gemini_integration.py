"""Legacy agent microservice (Flask).

This is the original ``generate`` / ``criticize`` / ``integrate`` HTTP service
that the Go orchestrator talks to on port 5000. It has been reworked to reuse
the shared multi-provider layer in ``app.providers`` instead of hard-coding
Google Gemini, so it now supports Gemini, OpenAI, Anthropic, OpenRouter, Groq
and the offline Mock provider.

For a single deployable service prefer the FastAPI app in ``app/main.py``; this
module is kept for the polyglot (Go + Python) local architecture.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, request

# Make the shared ``app`` package importable when run from this folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.orchestrator import (  # noqa: E402
    CRITIC_SYSTEM,
    GENERATOR_SYSTEM,
    INTEGRATOR_SYSTEM,
)
from app.providers import LLMMessage, ProviderError, get_provider  # noqa: E402

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DEFAULT_PROVIDER = os.getenv("ITERAMIND_PROVIDER", "mock")


def _complete(system: str, user: str, data: dict) -> str:
    provider = get_provider(
        data.get("provider", DEFAULT_PROVIDER),
        api_key=data.get("api_key"),
        model=data.get("model"),
    )

    async def _go() -> str:
        result = await provider.complete(
            [LLMMessage("system", system), LLMMessage("user", user)]
        )
        return result.text

    return asyncio.run(_go())


@app.post("/generate")
def generate():
    data = request.get_json(force=True) or {}
    prompt = data.get("prompt", "")
    logging.info("generate: %s", prompt)
    try:
        text = _complete(GENERATOR_SYSTEM, f"Task:\n{prompt}", data)
        return jsonify({"response": text, "generated_code": text}), 200
    except ProviderError as exc:
        logging.error("generate failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.post("/criticize")
def criticize():
    data = request.get_json(force=True) or {}
    code = data.get("code", "")
    logging.info("criticize: %s", code[:80])
    try:
        text = _complete(CRITIC_SYSTEM, f"Current solution:\n{code}", data)
        return jsonify({"response": text}), 200
    except ProviderError as exc:
        logging.error("criticize failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.post("/integrate")
def integrate():
    data = request.get_json(force=True) or {}
    code = data.get("code", "")
    feedback = data.get("feedback", "")
    logging.info("integrate")
    try:
        text = _complete(
            INTEGRATOR_SYSTEM,
            f"Current solution:\n{code}\n\nCritic feedback:\n{feedback}",
            data,
        )
        return jsonify({"response": text, "generated_code": text}), 200
    except ProviderError as exc:
        logging.error("integrate failed: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.get("/health")
def health():
    return jsonify({"status": "ok", "default_provider": DEFAULT_PROVIDER}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
