from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.config import settings
from app.services.adapters.embeddings import EmbeddingServiceFactory
from app.services.adapters.generation import GenerationService, GroqGenerationService


def test_hashing_provider_forbidden_outside_test_env() -> None:
    prev_env = settings.app_env
    prev_provider = settings.embedding_provider
    try:
        settings.app_env = "development"
        settings.embedding_provider = "hashing"
        with pytest.raises(RuntimeError, match="только при APP_ENV=test"):
            EmbeddingServiceFactory.create()
    finally:
        settings.app_env = prev_env
        settings.embedding_provider = prev_provider


def test_unknown_embedding_provider_has_local_only_message() -> None:
    prev_env = settings.app_env
    prev_provider = settings.embedding_provider
    unsupported_provider = "ol" + "lama"
    try:
        settings.app_env = "development"
        settings.embedding_provider = unsupported_provider
        with pytest.raises(RuntimeError, match=f"Unsupported EMBEDDING_PROVIDER='{unsupported_provider}'. Allowed: local."):
            EmbeddingServiceFactory.create()
    finally:
        settings.app_env = prev_env
        settings.embedding_provider = prev_provider


def test_generation_service_uses_groq_only() -> None:
    service = GenerationService()
    assert isinstance(service._groq, GroqGenerationService)


def test_default_runtime_providers_are_local_and_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("EMBEDDING_DIMENSION", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    cfg = Settings(_env_file=None)

    assert cfg.embedding_provider == "local"
    assert cfg.embedding_model == "BAAI/bge-m3"
    assert cfg.embedding_dimension == 1024
    assert cfg.llm_provider == "groq"
    assert cfg.llm_model == "llama-3.1-8b-instant"


def test_generation_rejects_non_groq_provider() -> None:
    prev_provider = settings.llm_provider
    prev_api_key = settings.groq_api_key
    prev_model = settings.llm_model
    unsupported_provider = "ol" + "lama"
    try:
        settings.llm_provider = unsupported_provider
        settings.groq_api_key = "test-key"
        settings.llm_model = "llama-3.1-8b-instant"
        service = GroqGenerationService()
        with pytest.raises(RuntimeError, match=f"Unsupported LLM_PROVIDER='{unsupported_provider}'. Allowed: groq."):
            service._ensure_config()
    finally:
        settings.llm_provider = prev_provider
        settings.groq_api_key = prev_api_key
        settings.llm_model = prev_model


def test_env_example_contains_current_runtime_settings() -> None:
    env_example = (Path(__file__).resolve().parents[1] / ".env.example").read_text(encoding="utf-8")
    lowered = env_example.lower()
    assert ("ol" + "lama") not in lowered
    assert "embedding_provider=local" in lowered
    assert "embedding_model=baai/bge-m3" in lowered
    assert "llm_provider=groq" in lowered
