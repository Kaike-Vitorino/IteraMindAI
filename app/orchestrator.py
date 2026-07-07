"""Iterative reasoning engine.

The core idea of IteraMindAI: instead of a single LLM call, a task is refined
across rounds by three cooperating roles, all backed by the same pluggable
provider:

    generator  -> produces an initial solution
    critic     -> reviews the current solution and lists concrete issues
    integrator -> rewrites the solution applying the critic's feedback

The loop stops after ``max_iterations`` rounds or early if the critic approves.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .providers import LLMMessage, LLMProvider

GENERATOR_SYSTEM = (
    "You are the Generator agent. Produce a clear, correct first solution to the "
    "user's task. Prefer working code in fenced blocks when the task is technical. "
    "Be concise; do not include commentary about your own process."
)

CRITIC_SYSTEM = (
    "You are the Critic agent. Rigorously review the current solution for the given "
    "task. List concrete, actionable issues covering correctness, edge cases, "
    "robustness, readability and performance. Be specific and terse. "
    "End with a verdict line: 'Verdict: APPROVED' if the solution is production "
    "ready with no material issues, otherwise 'Verdict: NEEDS_WORK'."
)

INTEGRATOR_SYSTEM = (
    "You are the Integrator agent. Rewrite the solution so it fully addresses every "
    "point raised by the critic, while preserving what already works. Return the "
    "complete improved solution (not a diff), with code in fenced blocks when "
    "relevant. Do not explain the changes at length."
)

APPROVAL_MARKERS = ("verdict: approved", "lgtm", "no material issues")


def _approved(feedback: str) -> bool:
    low = feedback.lower()
    return any(marker in low for marker in APPROVAL_MARKERS)


async def _ask(
    provider: LLMProvider,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: int,
) -> str:
    messages = [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user", content=user),
    ]
    result = await provider.complete(
        messages, temperature=temperature, max_tokens=max_tokens
    )
    return result.text.strip()


async def stream_iterations(
    task: str,
    provider: LLMProvider,
    *,
    max_iterations: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AsyncIterator[dict[str, Any]]:
    """Run the loop, yielding an event dict per step and a final ``done`` event."""
    model = provider.model
    pname = provider.name

    def step_event(iteration: int, role: str, content: str) -> dict[str, Any]:
        return {
            "type": "step",
            "step": {
                "iteration": iteration,
                "role": role,
                "content": content,
                "provider": pname,
                "model": model,
            },
        }

    steps: list[dict[str, Any]] = []
    stopped_early = False

    # --- Round 0: initial generation -------------------------------------
    current = await _ask(
        provider, GENERATOR_SYSTEM, f"Task:\n{task}",
        temperature=temperature, max_tokens=max_tokens,
    )
    ev = step_event(1, "generator", current)
    steps.append(ev["step"])
    yield ev

    # --- Refinement rounds ------------------------------------------------
    for i in range(1, max_iterations):
        critique = await _ask(
            provider,
            CRITIC_SYSTEM,
            f"Task:\n{task}\n\nCurrent solution:\n{current}",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        ev = step_event(i + 1, "critic", critique)
        steps.append(ev["step"])
        yield ev

        if _approved(critique):
            stopped_early = True
            break

        improved = await _ask(
            provider,
            INTEGRATOR_SYSTEM,
            f"Task:\n{task}\n\nCurrent solution:\n{current}\n\n"
            f"Critic feedback:\n{critique}",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        current = improved
        ev = step_event(i + 1, "integrator", current)
        steps.append(ev["step"])
        yield ev

    yield {
        "type": "done",
        "result": {
            "task": task,
            "provider": pname,
            "model": model,
            "iterations": len({s["iteration"] for s in steps}),
            "steps": steps,
            "final_solution": current,
            "stopped_early": stopped_early,
        },
    }


async def run_iterations(
    task: str,
    provider: LLMProvider,
    *,
    max_iterations: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Collect :func:`stream_iterations` into a single result dict."""
    result: dict[str, Any] = {}
    async for event in stream_iterations(
        task,
        provider,
        max_iterations=max_iterations,
        temperature=temperature,
        max_tokens=max_tokens,
    ):
        if event["type"] == "done":
            result = event["result"]
    return result
