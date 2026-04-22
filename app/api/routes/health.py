from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthOut, OllamaHealthOut
from app.services.adapters.ollama_client import OllamaClient

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/ollama", response_model=OllamaHealthOut)
def ollama_health() -> OllamaHealthOut:
    client = OllamaClient()
    reachable = client.is_available()
    models = client.list_models() if reachable else []
    required_models: list[str] = []
    if settings.embedding_provider.lower() == "ollama" and settings.ollama_embedding_model:
        required_models.append(settings.ollama_embedding_model)
    missing_models = [name for name in required_models if name and name not in models]
    if reachable:
        if missing_models:
            msg = (
                "Ollama is reachable, but required models are missing: "
                + ", ".join(missing_models)
                + ". Run: "
                + " && ".join(f"ollama pull {name}" for name in missing_models)
            )
            status = "degraded"
        else:
            msg = "Ollama is reachable and required models are available"
            status = "ok"
    else:
        msg = (
            f"Ollama is not reachable at {settings.ollama_base_url}. "
            "If backend is in Docker, use host.docker.internal."
        )
        status = "degraded"
    return OllamaHealthOut(
        status=status,
        base_url=settings.ollama_base_url,
        reachable=reachable,
        models=models,
        missing_models=missing_models,
        message=msg,
    )
