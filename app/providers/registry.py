"""Provider registry — resolves a provider slug to a configured instance.

Resolution order for the API key:
1. explicit ``api_key`` argument (e.g. from the request body),
2. the provider-specific environment variable,
3. nothing (fine for the keyless Mock provider; an error otherwise).
"""
from __future__ import annotations

import os

from .anthropic import AnthropicProvider
from .base import LLMProvider, ProviderError
from .gemini import GeminiProvider
from .groq import GroqProvider
from .mock import MockProvider
from .openai_provider import OpenAIProvider
from .openrouter import OpenRouterProvider

# slug -> (class, env var holding the key)
_REGISTRY: dict[str, tuple[type[LLMProvider], str | None]] = {
    "mock": (MockProvider, None),
    "gemini": (GeminiProvider, "GOOGLE_GEMINI_API_KEY"),
    "openai": (OpenAIProvider, "OPENAI_API_KEY"),
    "anthropic": (AnthropicProvider, "ANTHROPIC_API_KEY"),
    "openrouter": (OpenRouterProvider, "OPENROUTER_API_KEY"),
    "groq": (GroqProvider, "GROQ_API_KEY"),
}


def available_providers() -> list[dict]:
    """Metadata for the UI: which providers exist and whether a key is set."""
    out = []
    for slug, (cls, env) in _REGISTRY.items():
        out.append(
            {
                "name": slug,
                "label": cls.label,
                "default_model": cls.default_model,
                "requires_key": cls.requires_key,
                "key_configured": bool(env and os.getenv(env)),
            }
        )
    return out


def get_provider(
    name: str,
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 60.0,
) -> LLMProvider:
    """Build a configured provider instance by slug."""
    name = (name or "mock").lower().strip()
    if name not in _REGISTRY:
        raise ProviderError(
            f"Unknown provider '{name}'. Available: {', '.join(_REGISTRY)}"
        )
    cls, env = _REGISTRY[name]
    key = api_key or (os.getenv(env) if env else None)
    return cls(api_key=key, model=model, timeout=timeout)


def default_provider_name() -> str:
    """Pick a sensible default: first provider with a configured key, else mock."""
    for slug, (_cls, env) in _REGISTRY.items():
        if env and os.getenv(env):
            return slug
    return "mock"
