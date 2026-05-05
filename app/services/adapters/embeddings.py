from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_WORD_RE = re.compile(r"[A-Za-zА-Яа-я0-9_]+")


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


class BaseEmbeddingService(ABC):
    model_name: str
    dimension: int

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]


class HashingEmbeddingService(BaseEmbeddingService):
    def __init__(self, *, dimension: int, seed: str) -> None:
        self.dimension = dimension
        self.seed = seed
        self.model_name = f"hashing-{dimension}"

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = _WORD_RE.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.blake2b(f"{self.seed}:{token}".encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:8], "big") % self.dimension
            sign = 1.0 if digest[8] % 2 == 0 else -1.0
            vector[index] += sign

        return _normalize(vector)


class LocalEmbeddingService(BaseEmbeddingService):
    def __init__(self, *, model_name: str, configured_dimension: int) -> None:
        self.model_name = model_name
        self._model = self._load_model(model_name)
        if hasattr(self._model, "max_seq_length"):
            self._model.max_seq_length = settings.embedding_max_seq_length
        model_dimension = int(self._model.get_sentence_embedding_dimension() or 0)
        if model_dimension <= 0:
            raise RuntimeError(f"Не удалось определить размерность embedding-модели '{model_name}'.")
        if configured_dimension != model_dimension:
            raise RuntimeError(
                "EMBEDDING_DIMENSION не совпадает с моделью эмбеддингов: "
                f"env={configured_dimension}, model={model_dimension}, EMBEDDING_MODEL={model_name}."
            )
        self.dimension = model_dimension
        logger.info(
            "Local embeddings initialized model=%s model_dimension=%s max_seq_length=%s batch_size=%s",
            self.model_name,
            self.dimension,
            getattr(self._model, "max_seq_length", "<not-supported>"),
            settings.embedding_batch_size,
        )

    @staticmethod
    def _load_model(model_name: str) -> Any:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Пакет sentence-transformers не установлен. Добавьте зависимость и пересоберите окружение."
            ) from exc

        try:
            return SentenceTransformer(model_name)
        except Exception as exc:  # pragma: no cover - depends on runtime/model cache
            raise RuntimeError(
                f"Не удалось загрузить embedding-модель '{model_name}'. "
                "Проверьте EMBEDDING_MODEL и доступ к модели."
            ) from exc

    def embed_text(self, text: str) -> list[float]:
        batch = self.embed_batch([text])
        return batch[0] if batch else [0.0] * self.dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors = self._model.encode(
            texts,
            batch_size=settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return [[float(value) for value in row] for row in vectors]


class EmbeddingServiceFactory:
    @staticmethod
    def create() -> BaseEmbeddingService:
        provider = settings.embedding_provider.strip().lower()

        if provider == "local":
            logger.info(
                "Using local embeddings provider model=%s configured_dimension=%s max_seq_length=%s batch_size=%s",
                settings.embedding_model,
                settings.embedding_dimension,
                settings.embedding_max_seq_length,
                settings.embedding_batch_size,
            )
            return LocalEmbeddingService(
                model_name=settings.embedding_model,
                configured_dimension=settings.embedding_dimension,
            )

        if provider == "hashing":
            if settings.app_env.strip().lower() != "test":
                raise RuntimeError(
                    "EMBEDDING_PROVIDER=hashing разрешен только при APP_ENV=test. "
                    "Для development/production используйте EMBEDDING_PROVIDER=local."
                )
            logger.info("Using hashing embeddings for tests dim=%s", settings.embedding_dimension)
            return HashingEmbeddingService(
                dimension=settings.embedding_dimension,
                seed=settings.hash_embedding_seed,
            )

        raise RuntimeError(
            f"Неподдерживаемый EMBEDDING_PROVIDER='{settings.embedding_provider}'. "
            "Допустимо: local. Hashing разрешен только для APP_ENV=test."
        )
