from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.enums import AudienceLevel, CorpusType
from app.db.models import Version
from app.repositories.indexing import ChunkPayload, DocumentPayload, IndexingRepository
from app.services.adapters.embeddings import BaseEmbeddingService, EmbeddingServiceFactory
from app.services.ingestion.chunker import ChunkDraft, TextChunker
from app.services.ingestion.official_loader import OfficialDocumentationLoader, RawWebDocument
from app.services.ingestion.parser import ParagraphBlock, parse_html_document
from app.services.ingestion.supplementary_loader import RawSupplementaryDocument, SupplementaryCorpusLoader

logger = get_logger(__name__)


@dataclass(slots=True)
class ReindexStats:
    version: str
    official_documents: int = 0
    supplementary_documents: int = 0
    indexed_chunks: int = 0


@dataclass(slots=True)
class PreparedDocument:
    title: str
    source_url: str
    checksum: str
    corpus_type: str
    audience_level: str
    raw_html: str | None
    normalized_text: str
    chunk_drafts: list[ChunkDraft]


@dataclass(slots=True)
class CorpusSaveStats:
    documents: int = 0
    chunks: int = 0
    embeddings: int = 0
    embedding_batches_done: int = 0
    embedding_batches_planned: int = 0


class IndexingPipeline:
    def __init__(
        self,
        db: Session,
        *,
        embedding_batch_size: int | None = None,
        commit_every_docs: int = 25,
        progress_every: int = 10,
    ) -> None:
        self.db = db
        self.repo = IndexingRepository(db)
        self.embedding: BaseEmbeddingService = EmbeddingServiceFactory.create()
        self.chunker = TextChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
        self.official_loader = OfficialDocumentationLoader()
        self.supp_loader = SupplementaryCorpusLoader()

        self.embedding_batch_size = max(1, int(embedding_batch_size or settings.embedding_batch_size))
        self.commit_every_docs = max(1, int(commit_every_docs))
        self.progress_every = max(1, int(progress_every))

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
        logger.info(
            "Reindex version start version=%s include_official=%s include_supplementary=%s commit_every_docs=%s embedding_batch_size=%s progress_every=%s",
            version,
            include_official,
            include_supplementary,
            self.commit_every_docs,
            self.embedding_batch_size,
            self.progress_every,
        )

        docs_base_url = OfficialDocumentationLoader.build_base_url(version)
        version_row = self.repo.get_or_create_version(version, docs_base_url)
        # Close transaction before heavy CPU work.
        self.db.commit()

        stats = ReindexStats(version=version)

        if include_official:
            official_raw = self.official_loader.load_documents(version=version, max_pages=max_pages)
            official_stats = self._reindex_corpus(
                version_row=version_row,
                version=version,
                corpus_type=CorpusType.OFFICIAL.value,
                raw_documents=official_raw,
                prepare=self._prepare_official_document,
            )
            stats.official_documents = official_stats.documents
            stats.indexed_chunks += official_stats.chunks

        if include_supplementary:
            supplementary_raw = self.supp_loader.load_documents(version=version)
            supplementary_stats = self._reindex_corpus(
                version_row=version_row,
                version=version,
                corpus_type=CorpusType.SUPPLEMENTARY.value,
                raw_documents=supplementary_raw,
                prepare=self._prepare_supplementary_document,
            )
            stats.supplementary_documents = supplementary_stats.documents
            stats.indexed_chunks += supplementary_stats.chunks

        logger.info(
            "Reindex version completed version=%s official_docs=%s supplementary_docs=%s chunks=%s",
            stats.version,
            stats.official_documents,
            stats.supplementary_documents,
            stats.indexed_chunks,
        )
        return stats

    def _reindex_corpus(
        self,
        *,
        version_row: Version,
        version: str,
        corpus_type: str,
        raw_documents: list[Any],
        prepare: Callable[[Any, str], PreparedDocument | None],
    ) -> CorpusSaveStats:
        total_raw = len(raw_documents)
        logger.info(
            "Reindex started version=%s corpus_type=%s documents=%s",
            version,
            corpus_type,
            total_raw,
        )

        if total_raw == 0:
            logger.warning(
                "Reindex skipped version=%s corpus_type=%s reason=no source documents. Existing rows kept.",
                version,
                corpus_type,
            )
            return CorpusSaveStats()

        prepared_docs_total = 0
        generated_chunks_total = 0
        saved = CorpusSaveStats()
        delete_old_applied = False

        prepared_batch: list[PreparedDocument] = []

        for idx, raw in enumerate(raw_documents, start=1):
            prepared = prepare(raw, version)
            if prepared is None:
                if idx % self.progress_every == 0 or idx == total_raw:
                    logger.info(
                        "Chunking progress version=%s corpus_type=%s processed=%s/%s chunks=%s embedding_batches_planned=%s",
                        version,
                        corpus_type,
                        idx,
                        total_raw,
                        generated_chunks_total,
                        saved.embedding_batches_planned,
                    )
                continue

            prepared_batch.append(prepared)
            prepared_docs_total += 1
            generated_chunks_total += len(prepared.chunk_drafts)
            saved.embedding_batches_planned += self._count_embedding_batches(len(prepared.chunk_drafts))

            if idx % self.progress_every == 0 or idx == total_raw:
                logger.info(
                    "Chunking progress version=%s corpus_type=%s processed=%s/%s chunks=%s embedding_batches_planned=%s",
                    version,
                    corpus_type,
                    idx,
                    total_raw,
                    generated_chunks_total,
                    saved.embedding_batches_planned,
                )

            if len(prepared_batch) >= self.commit_every_docs:
                stage = self._save_prepared_batch(
                    version_row=version_row,
                    version=version,
                    corpus_type=corpus_type,
                    prepared_batch=prepared_batch,
                    apply_delete_old=not delete_old_applied,
                )
                delete_old_applied = True
                saved.documents += stage.documents
                saved.chunks += stage.chunks
                saved.embeddings += stage.embeddings
                saved.embedding_batches_done += stage.embedding_batches_done
                logger.info(
                    "DB cumulative progress version=%s corpus_type=%s documents_saved=%s chunks_saved=%s embeddings_saved=%s",
                    version,
                    corpus_type,
                    saved.documents,
                    saved.chunks,
                    saved.embeddings,
                )
                prepared_batch = []

        if prepared_batch:
            stage = self._save_prepared_batch(
                version_row=version_row,
                version=version,
                corpus_type=corpus_type,
                prepared_batch=prepared_batch,
                apply_delete_old=not delete_old_applied,
            )
            delete_old_applied = True
            saved.documents += stage.documents
            saved.chunks += stage.chunks
            saved.embeddings += stage.embeddings
            saved.embedding_batches_done += stage.embedding_batches_done
            logger.info(
                "DB cumulative progress version=%s corpus_type=%s documents_saved=%s chunks_saved=%s embeddings_saved=%s",
                version,
                corpus_type,
                saved.documents,
                saved.chunks,
                saved.embeddings,
            )

        if prepared_docs_total == 0:
            logger.warning(
                "Reindex skipped version=%s corpus_type=%s reason=no parseable documents. Existing rows kept.",
                version,
                corpus_type,
            )
            return CorpusSaveStats()

        logger.info(
            "Reindex completed version=%s corpus_type=%s documents=%s chunks=%s embeddings=%s embedding_batches=%s/%s",
            version,
            corpus_type,
            saved.documents,
            saved.chunks,
            saved.embeddings,
            saved.embedding_batches_done,
            saved.embedding_batches_planned,
        )
        return saved

    def _save_prepared_batch(
        self,
        *,
        version_row: Version,
        version: str,
        corpus_type: str,
        prepared_batch: list[PreparedDocument],
        apply_delete_old: bool,
    ) -> CorpusSaveStats:
        payloads: list[DocumentPayload] = []
        batch_planned = sum(self._count_embedding_batches(len(doc.chunk_drafts)) for doc in prepared_batch)
        batch_done = 0

        logger.info(
            "Embedding plan version=%s corpus_type=%s docs=%s batches=%s",
            version,
            corpus_type,
            len(prepared_batch),
            batch_planned,
        )

        for prepared in prepared_batch:
            chunk_payloads: list[ChunkPayload] = []
            if prepared.chunk_drafts:
                vectors, doc_batches = self._embed_chunk_texts(
                    [chunk.chunk_text for chunk in prepared.chunk_drafts],
                    version=version,
                    corpus_type=corpus_type,
                    batch_done_before=batch_done,
                    batch_total=batch_planned,
                )
                batch_done += doc_batches
                chunk_payloads = [
                    ChunkPayload(
                        chunk_index=chunk.chunk_index,
                        section_path=chunk.section_path,
                        chunk_text=chunk.chunk_text,
                        token_count=chunk.token_count,
                        content_type=chunk.content_type,
                        pedagogical_role=chunk.pedagogical_role,
                        embedding=vector,
                    )
                    for chunk, vector in zip(prepared.chunk_drafts, vectors, strict=True)
                ]

            payloads.append(
                DocumentPayload(
                    title=prepared.title,
                    source_url=prepared.source_url,
                    checksum=prepared.checksum,
                    corpus_type=prepared.corpus_type,
                    audience_level=prepared.audience_level,
                    raw_html=prepared.raw_html,
                    normalized_text=prepared.normalized_text,
                    chunks=chunk_payloads,
                )
            )

        try:
            if apply_delete_old:
                deleted_rows = self.repo.clear_version_corpus(version_row.id, corpus_type)
                logger.info(
                    "Deleted previous corpus rows version=%s corpus_type=%s documents_deleted=%s",
                    version,
                    corpus_type,
                    deleted_rows,
                )
            insert_stats = self.repo.insert_documents(
                version=version_row,
                embedding_model=self.embedding.model_name,
                embedding_dimension=self.embedding.dimension,
                documents=payloads,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        logger.info(
            "DB save progress version=%s corpus_type=%s documents_saved=%s chunks_saved=%s embeddings_saved=%s",
            version,
            corpus_type,
            insert_stats.documents_inserted,
            insert_stats.chunks_inserted,
            insert_stats.embeddings_inserted,
        )

        return CorpusSaveStats(
            documents=insert_stats.documents_inserted,
            chunks=insert_stats.chunks_inserted,
            embeddings=insert_stats.embeddings_inserted,
            embedding_batches_done=batch_done,
            embedding_batches_planned=batch_planned,
        )

    def _prepare_official_document(self, raw: RawWebDocument, version: str) -> PreparedDocument | None:
        parsed = parse_html_document(source_url=raw.source_url, html=raw.html)
        chunks = self.chunker.build_chunks(parsed.paragraphs)
        if not chunks:
            return None

        self._persist_artifacts(
            version=version,
            source_url=parsed.source_url,
            raw_content=parsed.raw_html,
            normalized_text=parsed.normalized_text,
        )

        return PreparedDocument(
            title=parsed.title,
            source_url=parsed.source_url,
            checksum=self._checksum(parsed.raw_html),
            corpus_type=CorpusType.OFFICIAL.value,
            audience_level=AudienceLevel.GENERAL.value,
            raw_html=parsed.raw_html,
            normalized_text=parsed.normalized_text,
            chunk_drafts=chunks,
        )

    def _prepare_supplementary_document(self, raw: RawSupplementaryDocument, version: str) -> PreparedDocument | None:
        paragraphs = self._text_to_paragraphs(title=raw.title, text=raw.text)
        chunks = self.chunker.build_chunks(paragraphs)
        if not chunks:
            return None

        normalized = "\n".join(f"[{p.section_path}] {p.text}" for p in paragraphs)
        self._persist_artifacts(
            version=version,
            source_url=raw.source_url,
            raw_content=raw.raw_content,
            normalized_text=normalized,
        )

        return PreparedDocument(
            title=raw.title,
            source_url=raw.source_url,
            checksum=self._checksum(raw.raw_content),
            corpus_type=CorpusType.SUPPLEMENTARY.value,
            audience_level=AudienceLevel.NOVICE.value,
            raw_html=raw.raw_content,
            normalized_text=normalized,
            chunk_drafts=chunks,
        )

    def _embed_chunk_texts(
        self,
        texts: list[str],
        *,
        version: str,
        corpus_type: str,
        batch_done_before: int,
        batch_total: int,
    ) -> tuple[list[list[float]], int]:
        vectors: list[list[float]] = []
        batches_done = 0

        for start in range(0, len(texts), self.embedding_batch_size):
            batch_texts = texts[start : start + self.embedding_batch_size]
            batch_vectors = self.embedding.embed_batch(batch_texts)
            if len(batch_vectors) != len(batch_texts):
                raise RuntimeError(
                    "Embedding service returned unexpected vector count: "
                    f"requested={len(batch_texts)} returned={len(batch_vectors)}"
                )
            vectors.extend(batch_vectors)
            batches_done += 1
            absolute_done = batch_done_before + batches_done
            if absolute_done % self.progress_every == 0 or absolute_done == batch_total:
                logger.info(
                    "Embedding progress version=%s corpus_type=%s batch=%s/%s",
                    version,
                    corpus_type,
                    absolute_done,
                    batch_total,
                )

        return vectors, batches_done

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

    def _count_embedding_batches(self, chunks_count: int) -> int:
        if chunks_count <= 0:
            return 0
        effective_batch = self.embedding_batch_size
        return int(math.ceil(chunks_count / effective_batch))

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
