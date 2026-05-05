from __future__ import annotations

import pytest

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


def test_generation_service_uses_groq_only() -> None:
    service = GenerationService()
    assert isinstance(service._groq, GroqGenerationService)
