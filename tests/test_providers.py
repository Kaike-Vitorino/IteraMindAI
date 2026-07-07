import pytest

from app.providers import (
    LLMMessage,
    ProviderError,
    available_providers,
    default_provider_name,
    get_provider,
)
from app.providers.mock import MockProvider


def test_registry_lists_all_providers():
    names = {p["name"] for p in available_providers()}
    assert {"mock", "gemini", "openai", "anthropic", "openrouter", "groq"} <= names


def test_default_provider_without_keys_is_mock(monkeypatch):
    for env in (
        "GOOGLE_GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "GROQ_API_KEY",
    ):
        monkeypatch.delenv(env, raising=False)
    assert default_provider_name() == "mock"


def test_get_unknown_provider_raises():
    with pytest.raises(ProviderError):
        get_provider("does-not-exist")


def test_gemini_uses_env_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "secret-123")
    p = get_provider("gemini")
    assert p.api_key == "secret-123"
    assert p.name == "gemini"


def test_request_key_overrides_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    p = get_provider("openai", api_key="req-key")
    assert p.api_key == "req-key"


@pytest.mark.asyncio
async def test_mock_provider_is_role_aware():
    p = MockProvider()
    gen = await p.complete([
        LLMMessage("system", "You are the Generator agent."),
        LLMMessage("user", "average of a list"),
    ])
    crit = await p.complete([
        LLMMessage("system", "You are the Critic agent, review code."),
        LLMMessage("user", "average of a list"),
    ])
    assert "```" in gen.text
    assert "Verdict" in crit.text
    assert gen.provider == "mock"


@pytest.mark.asyncio
async def test_mock_integrator_not_misclassified_as_critic():
    # The Integrator prompt mentions the critic; it must still render as an
    # integrator (produce a revised solution), not a review.
    from app.orchestrator import INTEGRATOR_SYSTEM

    p = MockProvider()
    out = await p.complete([
        LLMMessage("system", INTEGRATOR_SYSTEM),
        LLMMessage("user", "improve this"),
    ])
    assert "Changes applied" in out.text
    assert "Verdict" not in out.text


@pytest.mark.asyncio
async def test_mock_does_not_leak_broken_code_fence():
    p = MockProvider()
    out = await p.complete([
        LLMMessage("system", "You are the Critic agent."),
        LLMMessage("user", "```python\ndef f():\n    return 1\n```"),
    ])
    # Even iterations of ``` markers means no dangling/broken fence.
    assert out.text.count("```") % 2 == 0


def test_provider_requires_key_error():
    with pytest.raises(ProviderError):
        p = get_provider("openai", api_key=None)
        p._require_key()
