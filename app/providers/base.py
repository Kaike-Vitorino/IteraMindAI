"""Abstract base for pluggable LLM providers.

Every concrete provider (Gemini, OpenAI, Anthropic, OpenRouter, Groq, Mock)
implements a single async ``complete`` method over a normalized message list,
so the orchestrator never needs to know which vendor is behind it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    """A single chat message in the normalized cross-provider format."""

    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResult:
    """Normalized result returned by every provider."""

    text: str
    provider: str
    model: str
    raw: dict[str, Any] | None = field(default=None, repr=False)


class ProviderError(RuntimeError):
    """Raised when a provider call fails (network, auth, bad response)."""


class LLMProvider(ABC):
    """Base class all providers inherit from."""

    #: short slug used in the API/UI (e.g. "gemini")
    name: str = "base"
    #: human friendly label for the UI
    label: str = "Base"
    #: model used when the caller does not specify one
    default_model: str = ""
    #: whether an API key is required to use this provider
    requires_key: bool = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.model = model or self.default_model
        self.timeout = timeout

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResult:
        """Generate a completion for ``messages`` and return normalized text."""
        raise NotImplementedError

    # -- helpers shared by concrete providers -------------------------------

    def _require_key(self) -> str:
        if not self.api_key:
            raise ProviderError(
                f"Provider '{self.name}' requires an API key. "
                f"Set it in the request or via environment variable."
            )
        return self.api_key

    @staticmethod
    def _split_system(messages: list[LLMMessage]) -> tuple[str, list[LLMMessage]]:
        """Split out system messages (some vendors take them separately)."""
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        rest = [m for m in messages if m.role != "system"]
        return system, rest
