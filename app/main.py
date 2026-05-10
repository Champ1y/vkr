from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import SessionLocal
from app.repositories.versions import VersionRepository
from app.schemas.common import EmbeddingsHealthOut, HealthOut
from app.api.routes.health import embeddings_health

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"


def seed_versions() -> None:
    with SessionLocal() as db:
        repo = VersionRepository(db)
        repo.ensure_seed_versions(settings.supported_versions)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.raw_docs_path.mkdir(parents=True, exist_ok=True)
    settings.normalized_docs_path.mkdir(parents=True, exist_ok=True)
    seed_versions()
    logger.info(
        "Generation configuration: llm_provider=%s groq_base_url=%s llm_model=%s embedding_provider=%s embedding_model=%s dim=%s",
        settings.llm_provider,
        settings.groq_base_url,
        settings.llm_model or "<unset>",
        settings.embedding_provider,
        settings.embedding_model,
        settings.embedding_dimension,
    )
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="PostgreSQL Assistant",
    description="Intelligent assistant for PostgreSQL documentation with version filtering",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", timestamp=datetime.now(timezone.utc))


@app.get("/health/embeddings", response_model=EmbeddingsHealthOut)
def health_embeddings() -> EmbeddingsHealthOut:
    return embeddings_health()


@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": "PostgreSQL RAG Assistant"},
        headers={"Cache-Control": "no-store"},
    )


@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "app_name": "PostgreSQL RAG Assistant"},
        headers={"Cache-Control": "no-store"},
    )
