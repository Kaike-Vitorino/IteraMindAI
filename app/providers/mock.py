"""Deterministic offline provider.

The Mock provider requires no API key and no network access, so the deployed
demo (and the test suite) works out of the box. It produces plausible,
role-aware text so the iterative loop is fully demonstrable without spending
tokens on a real vendor.
"""
from __future__ import annotations

import hashlib
import textwrap

from .base import LLMMessage, LLMProvider, LLMResult


class MockProvider(LLMProvider):
    name = "mock"
    label = "Mock (offline demo)"
    default_model = "mock-1"
    requires_key = False

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResult:
        system, rest = self._split_system(messages)
        last_user = next(
            (m.content for m in reversed(rest) if m.role == "user"), ""
        )
        seed = hashlib.sha256((system + last_user).encode()).hexdigest()[:8]
        role = self._infer_role(system)
        text = self._render(role, last_user, seed)
        return LLMResult(text=text, provider=self.name, model=self.model, raw=None)

    # -- internal -----------------------------------------------------------

    @staticmethod
    def _infer_role(system: str) -> str:
        # Match the explicit agent identity from the orchestrator prompts so the
        # word "critic" inside the Integrator prompt does not misclassify it.
        s = system.lower()
        if "integrator agent" in s:
            return "integrator"
        if "critic agent" in s:
            return "critic"
        return "generator"

    def _render(self, role: str, user: str, seed: str) -> str:
        # Strip backticks so an echoed code fence can't break rendering.
        clean = user.replace("\n", " ").replace("`", "").strip()
        snippet = textwrap.shorten(clean, width=140) or "the task"
        if role == "critic":
            return textwrap.dedent(
                f"""
                Review (mock, seed {seed}):
                - Correctness: the approach addresses "{snippet}" but lacks edge-case handling.
                - Robustness: add input validation and guard against empty/invalid input.
                - Clarity: naming is acceptable; add a short docstring and one example.
                - Verdict: NEEDS_WORK — apply the three points above.
                """
            ).strip()
        if role == "integrator":
            return textwrap.dedent(
                f"""
                ```python
                # Revised solution (mock, seed {seed})
                def solution(data):
                    \"\"\"Handles: {snippet}.\"\"\"
                    if not data:
                        raise ValueError("input must not be empty")
                    return sum(data) / len(data)
                ```
                Changes applied: added validation, docstring, and an edge-case guard.
                """
            ).strip()
        return textwrap.dedent(
            f"""
            ```python
            # Initial solution (mock, seed {seed})
            def solution(data):
                return sum(data) / len(data)
            ```
            First pass at: {snippet}. Not yet validated for edge cases.
            """
        ).strip()
