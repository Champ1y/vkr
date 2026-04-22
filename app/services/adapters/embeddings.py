from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.services.adapters.ollama_client import OllamaClient

logger = get_logger(__name__)

_WORD_RE = re.compile(r"[A-Za-zА-Яа-я0-9_]+")


def _resize_vector(vector: list[float], target_dim: int) -> list[float]:
    if len(vector) == target_dim:
        return vector
    if len(vector) > target_dim:
        return vector[:target_dim]
    return vector + [0.0] * (target_dim - len(vector))


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


class OpenAIEmbeddingService(BaseEmbeddingService):
    def __init__(self, *, api_key: str, model_name: str, dimension: int) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model_name, input=[text])
        vector = list(response.data[0].embedding)
        return _normalize(_resize_vector(vector, self.dimension))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        vectors = []
        for item in response.data:
            vector = list(item.embedding)
            vectors.append(_normalize(_resize_vector(vector, self.dimension)))
        return vectors


class OllamaEmbeddingService(BaseEmbeddingService):
    def __init__(self, *, model_name: str, dimension: int) -> None:
        self.client = OllamaClient()
        self.model_name = model_name
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        vectors = self.embed_batch([text])
        return vectors[0] if vectors else [0.0] * self.dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self.client.embed(model=self.model_name, texts=texts)
        return [_normalize(_resize_vector(list(vector), self.dimension)) for vector in vectors]


class EmbeddingServiceFactory:
    @staticmethod
    def create() -> BaseEmbeddingService:
        provider = settings.embedding_provider.strip().lower()

        if provider == "ollama":
            logger.info("Using Ollama embeddings model=%s", settings.ollama_embedding_model)
            return OllamaEmbeddingService(
                model_name=settings.ollama_embedding_model,
                dimension=settings.embedding_dimension,
            )

        if provider == "openai" and settings.openai_api_key:
            logger.info("Using OpenAI embeddings model=%s", settings.openai_embedding_model)
            return OpenAIEmbeddingService(
                api_key=settings.openai_api_key,
                model_name=settings.openai_embedding_model,
                dimension=settings.embedding_dimension,
            )

        if settings.use_openai_embeddings and settings.openai_api_key:
            logger.info("Using OpenAI embeddings model=%s (legacy flag)", settings.openai_embedding_model)
            return OpenAIEmbeddingService(
                api_key=settings.openai_api_key,
                model_name=settings.openai_embedding_model,
                dimension=settings.embedding_dimension,
            )

        if provider not in {"hashing", ""}:
            logger.warning("Unknown embedding provider '%s', fallback to hashing", provider)

        logger.info("Using local hashing embeddings dim=%s", settings.embedding_dimension)
        return HashingEmbeddingService(
            dimension=settings.embedding_dimension,
            seed=settings.hash_embedding_seed,
        )
