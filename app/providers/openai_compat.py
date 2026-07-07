"""Shared implementation for OpenAI-compatible chat APIs.

OpenAI, Groq, and OpenRouter all expose the same ``/chat/completions`` schema,
so they differ only by base URL, default model, and a couple of headers.
"""
from __future__ import annotations

import httpx

from .base import LLMMessage, LLMProvider, LLMResult, ProviderError


class OpenAICompatibleProvider(LLMProvider):
    #: subclasses override the base URL (up to, not including, /chat/completions)
    base_url: str = "https://api.openai.com/v1"

    def _extra_headers(self) -> dict[str, str]:
        return {}

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResult:
        key = self._require_key()
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            **self._extra_headers(),
        }
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise ProviderError(f"{self.label} error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected {self.label} response: {data}") from exc
        return LLMResult(text=text, provider=self.name, model=self.model, raw=data)
