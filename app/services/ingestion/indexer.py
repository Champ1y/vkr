from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.enums import AudienceLevel, CorpusType
from app.repositories.indexing import ChunkPayload, DocumentPayload, IndexingRepository
from app.services.adapters.embeddings import BaseEmbeddingService, EmbeddingServiceFactory
from app.services.ingestion.chunker import TextChunker
from app.services.ingestion.official_loader import OfficialDocumentationLoader
from app.services.ingestion.parser import ParagraphBlock, parse_html_document
from app.services.ingestion.supplementary_loader import SupplementaryCorpusLoader

logger = get_logger(__name__)


@dataclass(slots=True)
class ReindexStats:
    version: str
    official_documents: int = 0
    supplementary_documents: int = 0
    indexed_chunks: int = 0


class IndexingPipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = IndexingRepository(db)
        self.embedding: BaseEmbeddingService = EmbeddingServiceFactory.create()
        self.chunker = TextChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
        self.official_loader = OfficialDocumentationLoader()
        self.supp_loader = SupplementaryCorpusLoader()

        settings.raw_docs_path.mkdir(parents=True, exist_ok=True)
        settings.normalized_docs_path.mkdir(parents=True, exist_ok=True)

    def reindex_version(
        self,
        *,
        version: str,
        include_official: bool,
        include_supplementary: bool,
        max_pages: int | None = None,
    ) -> ReindexStats:
        docs_base_url = OfficialDocumentationLoader.build_base_url(version)
        version_row = self.repo.get_or_create_version(version, docs_base_url)
        stats = ReindexStats(version=version)

        if include_official:
            self.repo.clear_version_corpus(version_row.id, CorpusType.OFFICIAL.value)
            official_docs = self._build_official_documents(version=version, max_pages=max_pages)
            stats.official_documents = len(official_docs)
            stats.indexed_chunks += self.repo.insert_documents(
                version=version_row,
                embedding_model=self.embedding.model_name,
                embedding_dimension=self.embedding.dimension,
                documents=official_docs,
            )

        if include_supplementary:
            self.repo.clear_version_corpus(version_row.id, CorpusType.SUPPLEMENTARY.value)
            supplementary_docs = self._build_supplementary_documents(version=version)
            stats.supplementary_documents = len(supplementary_docs)
            stats.indexed_chunks += self.repo.insert_documents(
                version=version_row,
                embedding_model=self.embedding.model_name,
                embedding_dimension=self.embedding.dimension,
                documents=supplementary_docs,
            )

        self.db.commit()
        logger.info(
            "Reindex done version=%s official_docs=%s supplementary_docs=%s chunks=%s",
            stats.version,
            stats.official_documents,
            stats.supplementary_documents,
            stats.indexed_chunks,
        )
        return stats

    def _build_official_documents(self, *, version: str, max_pages: int | None) -> list[DocumentPayload]:
        documents = self.official_loader.load_documents(version=version, max_pages=max_pages)
        payloads: list[DocumentPayload] = []

        for raw in documents:
            parsed = parse_html_document(source_url=raw.source_url, html=raw.html)
            chunks = self.chunker.build_chunks(parsed.paragraphs)
            if not chunks:
                continue

            embeddings = self.embedding.embed_batch([chunk.chunk_text for chunk in chunks])
            chunk_payloads = [
                ChunkPayload(
                    chunk_index=chunk.chunk_index,
                    section_path=chunk.section_path,
                    chunk_text=chunk.chunk_text,
                    token_count=chunk.token_count,
                    content_type=chunk.content_type,
                    pedagogical_role=chunk.pedagogical_role,
                    embedding=embedding,
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]

            self._persist_artifacts(
                version=version,
                source_url=parsed.source_url,
                raw_content=parsed.raw_html,
                normalized_text=parsed.normalized_text,
            )

            payloads.append(
                DocumentPayload(
                    title=parsed.title,
                    source_url=parsed.source_url,
                    checksum=self._checksum(parsed.raw_html),
                    corpus_type=CorpusType.OFFICIAL.value,
                    audience_level=AudienceLevel.GENERAL.value,
                    raw_html=parsed.raw_html,
                    normalized_text=parsed.normalized_text,
                    chunks=chunk_payloads,
                )
            )

        return payloads

    def _build_supplementary_documents(self, *, version: str) -> list[DocumentPayload]:
        documents = self.supp_loader.load_documents(version=version)
        payloads: list[DocumentPayload] = []

        for raw in documents:
            paragraphs = self._text_to_paragraphs(title=raw.title, text=raw.text)
            chunks = self.chunker.build_chunks(paragraphs)
            if not chunks:
                continue

            embeddings = self.embedding.embed_batch([chunk.chunk_text for chunk in chunks])
            chunk_payloads = [
                ChunkPayload(
                    chunk_index=chunk.chunk_index,
                    section_path=chunk.section_path,
                    chunk_text=chunk.chunk_text,
                    token_count=chunk.token_count,
                    content_type=chunk.content_type,
                    pedagogical_role=chunk.pedagogical_role,
                    embedding=embedding,
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]

            normalized = "\n".join(f"[{p.section_path}] {p.text}" for p in paragraphs)
            self._persist_artifacts(
                version=version,
                source_url=raw.source_url,
                raw_content=raw.raw_content,
                normalized_text=normalized,
            )

            payloads.append(
                DocumentPayload(
                    title=raw.title,
                    source_url=raw.source_url,
                    checksum=self._checksum(raw.raw_content),
                    corpus_type=CorpusType.SUPPLEMENTARY.value,
                    audience_level=AudienceLevel.NOVICE.value,
                    raw_html=raw.raw_content,
                    normalized_text=normalized,
                    chunks=chunk_payloads,
                )
            )

        return payloads

    def _persist_artifacts(self, *, version: str, source_url: str, raw_content: str, normalized_text: str) -> None:
        slug = self._safe_slug(source_url)
        raw_dir = settings.raw_docs_path / version
        norm_dir = settings.normalized_docs_path / version
        raw_dir.mkdir(parents=True, exist_ok=True)
        norm_dir.mkdir(parents=True, exist_ok=True)

        (raw_dir / f"{slug}.html").write_text(raw_content, encoding="utf-8", errors="ignore")
        (norm_dir / f"{slug}.txt").write_text(normalized_text, encoding="utf-8", errors="ignore")

    @staticmethod
    def _safe_slug(source_url: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9]+", "_", source_url)
        return cleaned[:120].strip("_") or "doc"

    @staticmethod
    def _checksum(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    @staticmethod
    def _text_to_paragraphs(*, title: str, text: str) -> list[ParagraphBlock]:
        blocks: list[ParagraphBlock] = []
        for segment in text.split("\n\n"):
            normalized = " ".join(segment.split())
            if len(normalized) < 20:
                continue
            blocks.append(ParagraphBlock(section_path=title, text=normalized, content_type="paragraph"))

        if not blocks and text.strip():
            blocks.append(ParagraphBlock(section_path=title, text=" ".join(text.split()), content_type="paragraph"))

        return blocks
