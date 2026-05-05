from __future__ import annotations

import importlib.util
from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import EmbeddingsHealthOut, HealthOut

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/embeddings", response_model=EmbeddingsHealthOut)
def embeddings_health() -> EmbeddingsHealthOut:
    provider = settings.embedding_provider.strip().lower()
    app_env = settings.app_env.strip().lower()
    expected_msg = "Для BAAI/bge-m3 ожидается configured_dimension=1024 (dense mode only; sparse/ColBERT не используются)."

    if provider == "local":
        st_available = importlib.util.find_spec("sentence_transformers") is not None
        if not st_available:
            return EmbeddingsHealthOut(
                status="degraded",
                provider="local",
                model=settings.embedding_model,
                configured_dimension=settings.embedding_dimension,
                max_seq_length=settings.embedding_max_seq_length,
                batch_size=settings.embedding_batch_size,
                app_env=app_env,
                message=(
                    "Локальный provider выбран, но пакет sentence-transformers не установлен. "
                    "Пересоберите backend-образ: docker compose build --no-cache backend. "
                    + expected_msg
                ),
            )
        return EmbeddingsHealthOut(
            status="ok",
            provider="local",
            model=settings.embedding_model,
            configured_dimension=settings.embedding_dimension,
            max_seq_length=settings.embedding_max_seq_length,
            batch_size=settings.embedding_batch_size,
            app_env=app_env,
            message=f"Локальный embedding provider активен. {expected_msg}",
        )

    if provider == "hashing":
        status = "ok" if app_env == "test" else "degraded"
        message = (
            "Hashing provider активен для тестового окружения."
            if app_env == "test"
            else "Hashing provider разрешен только при APP_ENV=test."
        )
        return EmbeddingsHealthOut(
            status=status,
            provider="hashing",
            model=f"hashing-{settings.embedding_dimension}",
            configured_dimension=settings.embedding_dimension,
            max_seq_length=settings.embedding_max_seq_length,
            batch_size=settings.embedding_batch_size,
            app_env=app_env,
            message=f"{message} {expected_msg}",
        )

    return EmbeddingsHealthOut(
        status="degraded",
        provider=provider or "<unset>",
        model=settings.embedding_model,
        configured_dimension=settings.embedding_dimension,
        max_seq_length=settings.embedding_max_seq_length,
        batch_size=settings.embedding_batch_size,
        app_env=app_env,
        message=(
            "Неподдерживаемый EMBEDDING_PROVIDER. Допустимо: local "
            "(hashing только для APP_ENV=test). "
            + expected_msg
        ),
    )
