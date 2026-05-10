from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_postgres",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")

    supported_pg_versions: str = Field(default="16,17,18", alias="SUPPORTED_PG_VERSIONS")
    official_docs_base_url: str = Field(default="https://www.postgresql.org/docs", alias="OFFICIAL_DOCS_BASE_URL")
    official_crawl_max_pages: int = Field(default=40, alias="OFFICIAL_CRAWL_MAX_PAGES")
    official_request_timeout: int = Field(default=20, alias="OFFICIAL_REQUEST_TIMEOUT")

    chunk_size: int = Field(default=1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=18, alias="RETRIEVAL_TOP_K")
    rerank_top_k: int = Field(default=8, alias="RERANK_TOP_K")
    embedding_dimension: int = Field(default=1024, alias="EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(default=8, alias="EMBEDDING_BATCH_SIZE")
    embedding_max_seq_length: int = Field(default=8192, alias="EMBEDDING_MAX_SEQ_LENGTH")
    hash_embedding_seed: str = Field(default="postgres-rag", alias="HASH_EMBEDDING_SEED")

    # --- LLM generation (Groq runtime provider) ---
    llm_provider: str = Field(default="groq", alias="LLM_PROVIDER")
    llm_model: str = Field(
        default="llama-3.1-8b-instant",
        alias="LLM_MODEL",
    )
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")

    # --- Embedding provider ---
    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        default="BAAI/bge-m3",
        alias="EMBEDDING_MODEL",
    )

    # --- Corpus & data dirs ---
    corpus_dir: str = Field(default="corpus", alias="CORPUS_DIR")
    supplementary_dir: str = Field(default="corpus/tutorial", alias="SUPPLEMENTARY_DIR")
    raw_docs_dir: str = Field(default="data/raw_docs", alias="RAW_DOCS_DIR")
    normalized_docs_dir: str = Field(default="data/normalized_docs", alias="NORMALIZED_DOCS_DIR")

    admin_api_key: str = Field(default="", alias="ADMIN_API_KEY")

    @property
    def supported_versions(self) -> list[str]:
        return [v.strip() for v in self.supported_pg_versions.split(",") if v.strip()]

    @property
    def corpus_path(self) -> Path:
        return Path(self.corpus_dir)

    @property
    def raw_docs_path(self) -> Path:
        return Path(self.raw_docs_dir)

    @property
    def normalized_docs_path(self) -> Path:
        return Path(self.normalized_docs_dir)

    @property
    def supplementary_path(self) -> Path:
        return Path(self.supplementary_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
