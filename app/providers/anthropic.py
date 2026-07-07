"""Anthropic provider (Claude models, Messages API)."""
from __future__ import annotations

import httpx

from .base import LLMMessage, LLMProvider, LLMResult, ProviderError


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    label = "Anthropic Claude"
    default_model = "claude-3-5-haiku-latest"
    requires_key = True

    URL = "https://api.anthropic.com/v1/messages"
    VERSION = "2023-06-01"

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResult:
        key = self._require_key()
        system, rest = self._split_system(messages)

        payload: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": m.role, "content": m.content} for m in rest
            ],
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": key,
            "anthropic-version": self.VERSION,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise ProviderError(f"Anthropic error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            text = "".join(
                block["text"] for block in data["content"] if block.get("type") == "text"
            )
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Unexpected Anthropic response: {data}") from exc
        return LLMResult(text=text, provider=self.name, model=self.model, raw=data)
