from __future__ import annotations

from types import SimpleNamespace

from app.repositories.indexing import InsertStats
from app.services.ingestion.indexer import IndexingPipeline
from app.services.ingestion.official_loader import RawWebDocument


class _FakeDB:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")


class _FakeEmbeddingService:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.model_name = "hashing-4"
        self.dimension = 4

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.events.append(f"embed:{len(texts)}")
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]



def test_reindex_embeds_before_delete_and_commits_in_short_windows(monkeypatch) -> None:
    events: list[str] = []

    monkeypatch.setattr(
        "app.services.ingestion.indexer.EmbeddingServiceFactory.create",
        lambda: _FakeEmbeddingService(events),
    )

    pipeline = IndexingPipeline(
        _FakeDB(events),
        embedding_batch_size=2,
        commit_every_docs=1,
        progress_every=1,
    )

    monkeypatch.setattr(pipeline, "_persist_artifacts", lambda **_: None)

    pipeline.repo.get_or_create_version = lambda major_version, docs_base_url: SimpleNamespace(id="v16")  # type: ignore[method-assign]

    def fake_clear(version_id, corpus_type):  # type: ignore[no-untyped-def]
        events.append(f"clear:{corpus_type}")
        return 1

    def fake_insert(*, version, embedding_model, embedding_dimension, documents):  # type: ignore[no-untyped-def]
        events.append(f"insert:{len(documents)}")
        chunks = sum(len(doc.chunks) for doc in documents)
        return InsertStats(documents_inserted=len(documents), chunks_inserted=chunks, embeddings_inserted=chunks)

    pipeline.repo.clear_version_corpus = fake_clear  # type: ignore[method-assign]
    pipeline.repo.insert_documents = fake_insert  # type: ignore[method-assign]

    docs = [
        RawWebDocument(
            source_url="https://www.postgresql.org/docs/16/a.html",
            html="<html><body><h1>A</h1><p>" + ("alpha " * 20) + "</p></body></html>",
        ),
        RawWebDocument(
            source_url="https://www.postgresql.org/docs/16/b.html",
            html="<html><body><h1>B</h1><p>" + ("beta " * 20) + "</p></body></html>",
        ),
    ]
    monkeypatch.setattr(pipeline.official_loader, "load_documents", lambda version, max_pages=None: docs)

    pipeline.reindex_version(version="16", include_official=True, include_supplementary=False)

    # First commit closes transaction opened for version row resolution before heavy CPU work.
    assert events[0] == "commit"

    clear_pos = next(i for i, item in enumerate(events) if item.startswith("clear:"))
    embed_pos = next(i for i, item in enumerate(events) if item.startswith("embed:"))
    assert embed_pos < clear_pos

    # One commit for version bootstrap + one commit per saved batch (commit_every_docs=1, 2 docs -> 2 batches).
    assert events.count("commit") == 3
    assert events.count("rollback") == 0
