"""OpenAI provider (GPT models)."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    label = "OpenAI"
    default_model = "gpt-4o-mini"
    requires_key = True
    base_url = "https://api.openai.com/v1"
