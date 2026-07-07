"""Google Gemini provider (Generative Language API)."""
from __future__ import annotations

import httpx

from .base import LLMMessage, LLMProvider, LLMResult, ProviderError


class GeminiProvider(LLMProvider):
    name = "gemini"
    label = "Google Gemini"
    default_model = "gemini-1.5-flash-latest"
    requires_key = True

    BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResult:
        key = self._require_key()
        system, rest = self._split_system(messages)

        contents = []
        for m in rest:
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{self.BASE}/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, params={"key": key}, json=payload)
        if resp.status_code != 200:
            raise ProviderError(f"Gemini error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected Gemini response: {data}") from exc
        return LLMResult(text=text, provider=self.name, model=self.model, raw=data)
