"""OpenRouter provider (OpenAI-compatible gateway to many models)."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    label = "OpenRouter"
    default_model = "openai/gpt-4o-mini"
    requires_key = True
    base_url = "https://openrouter.ai/api/v1"

    def _extra_headers(self) -> dict[str, str]:
        # Optional attribution headers recommended by OpenRouter.
        return {
            "HTTP-Referer": "https://github.com/Kaike-Vitorino/IteraMindAI",
            "X-Title": "IteraMindAI",
        }
