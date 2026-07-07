"""Groq provider (OpenAI-compatible, very fast inference)."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    label = "Groq"
    default_model = "llama-3.3-70b-versatile"
    requires_key = True
    base_url = "https://api.groq.com/openai/v1"
