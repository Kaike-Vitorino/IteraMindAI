import pytest

from app.orchestrator import run_iterations, stream_iterations
from app.providers.base import LLMMessage, LLMProvider, LLMResult
from app.providers.mock import MockProvider


class ApprovingProvider(LLMProvider):
    """Critic always approves, so the loop must stop early."""

    name = "approver"
    default_model = "approver-1"
    requires_key = False

    async def complete(self, messages, *, temperature=0.7, max_tokens=1024):
        system, _ = self._split_system(messages)
        if "critic" in system.lower():
            text = "Looks great. Verdict: APPROVED"
        else:
            text = "some solution"
        return LLMResult(text=text, provider=self.name, model=self.model)


@pytest.mark.asyncio
async def test_run_iterations_shape():
    result = await run_iterations("compute average", MockProvider(), max_iterations=3)
    assert result["provider"] == "mock"
    assert result["final_solution"]
    roles = [s["role"] for s in result["steps"]]
    assert roles[0] == "generator"
    assert "critic" in roles
    assert "integrator" in roles


@pytest.mark.asyncio
async def test_single_iteration_only_generates():
    result = await run_iterations("hello", MockProvider(), max_iterations=1)
    assert len(result["steps"]) == 1
    assert result["steps"][0]["role"] == "generator"


@pytest.mark.asyncio
async def test_early_stop_on_approval():
    result = await run_iterations("x", ApprovingProvider(), max_iterations=5)
    assert result["stopped_early"] is True
    # generator + one critic (approved) => no integrator ran
    roles = [s["role"] for s in result["steps"]]
    assert roles == ["generator", "critic"]


@pytest.mark.asyncio
async def test_stream_emits_done_event():
    events = [e async for e in stream_iterations("x", MockProvider(), max_iterations=2)]
    assert events[-1]["type"] == "done"
    assert any(e["type"] == "step" for e in events)
