from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.adapters.embeddings import LocalEmbeddingService
from app.services.ingestion.supplementary_loader import SupplementaryCorpusLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_config_bge_m3_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("EMBEDDING_DIMENSION", raising=False)
    monkeypatch.delenv("EMBEDDING_BATCH_SIZE", raising=False)
    monkeypatch.delenv("EMBEDDING_MAX_SEQ_LENGTH", raising=False)

    cfg = Settings(_env_file=None)

    assert cfg.embedding_model == "BAAI/bge-m3"
    assert cfg.embedding_dimension == 1024
    assert cfg.embedding_batch_size == 8
    assert cfg.embedding_max_seq_length == 8192


def test_supplementary_loader_reads_corpus_tutorial_allowlist(tmp_path: Path) -> None:
    root = tmp_path / "corpus" / "tutorial"

    _write(
        root / "curated" / "16" / "intro.md",
        """---
title: "Curated Intro"
pg_version: "16"
source_role: "curated_learning"
---

# Curated Intro

Body for curated document that must be embedded.
""",
    )
    _write(
        root / "curated" / "16" / "wrong_version.md",
        """---
title: "Wrong version"
pg_version: "17"
---

Should be skipped because pg_version mismatches.
""",
    )

    _write(
        root / "processed_html" / "postgres_wiki_whitelist" / "wiki" / "Warm_Standby.md",
        """---
title: "Warm Standby - PostgreSQL wiki"
source_url: "https://wiki.postgresql.org/wiki/Warm_Standby"
original_html_path: "html/postgres_wiki_whitelist/wiki/Warm_Standby.html"
indexable: true
---

Processed markdown body for warm standby that should be indexed.
""",
    )
    _write(
        root / "processed_html" / "postgres_wiki_whitelist" / "wiki" / "skip.md",
        """---
title: "Skip"
source_url: "https://wiki.postgresql.org/wiki/Skip"
indexable: false
---

This page is not indexable.
""",
    )

    # Must not be indexed by allowlist policy.
    _write(root / "html" / "postgres_wiki_whitelist" / "wiki" / "raw.html", "<h1>Raw HTML</h1>")
    _write(root / "external_registry" / "note.md", "Should not be indexed")
    _write(root / "scripts" / "helper.md", "Should not be indexed")
    _write(root / "QUALITY_REPORT.md", "Should not be indexed")
    _write(root / "QUALITY_MANIFEST.md", "Should not be indexed")

    loader = SupplementaryCorpusLoader(root_dir=root)
    docs = loader.load_documents(version="16")

    assert len(docs) == 2

    curated = next(doc for doc in docs if doc.source_url.startswith("supplementary://curated/16/"))
    processed = next(doc for doc in docs if doc.source_url.startswith("https://wiki.postgresql.org/wiki/"))

    assert curated.title == "Curated Intro"
    assert "title:" not in curated.text
    assert not curated.text.lstrip().startswith("---")
    assert "Body for curated document" in curated.text

    assert processed.source_url == "https://wiki.postgresql.org/wiki/Warm_Standby"
    assert processed.title == "Warm Standby - PostgreSQL wiki"
    assert "source_url:" not in processed.text
    assert not processed.text.lstrip().startswith("---")

    text_blob = "\n".join(doc.text for doc in docs)
    assert "Raw HTML" not in text_blob
    assert "Should not be indexed" not in text_blob


class _FakeModel:
    def __init__(self) -> None:
        self.max_seq_length = 0

    def get_sentence_embedding_dimension(self) -> int:
        return 1024



def test_embedding_dimension_mismatch_still_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(LocalEmbeddingService, "_load_model", staticmethod(lambda _: _FakeModel()))

    with pytest.raises(RuntimeError, match="EMBEDDING_DIMENSION не совпадает"):
        LocalEmbeddingService(model_name="BAAI/bge-m3", configured_dimension=768)
