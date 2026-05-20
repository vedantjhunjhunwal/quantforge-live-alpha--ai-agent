import os

from quantforge.llm import LLMClient, LLMConfig
from quantforge.llm.client import LLMConfigurationError


def test_auto_provider_falls_back_to_deterministic_without_keys(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = LLMClient(LLMConfig(provider="auto"))
    assert client.provider == "deterministic"


def test_selected_openai_falls_back_when_enabled(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient(LLMConfig(provider="openai", allow_deterministic_fallback=True))
    assert client.provider == "deterministic"


def test_selected_openai_strict_does_not_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient(LLMConfig(provider="openai", allow_deterministic_fallback=False))
    assert client.provider == "openai"
