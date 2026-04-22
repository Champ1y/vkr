from __future__ import annotations

from pathlib import Path

from app.services.ingestion.official_loader import OfficialDocumentationLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_official_loader_reads_local_corpus(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    _write(corpus_root / "16" / "index.html", "<html><body><h1>Index</h1></body></html>")
    _write(corpus_root / "16" / "sql" / "select.html", "<html><body><h1>Select</h1></body></html>")

    loader = OfficialDocumentationLoader(corpus_root=corpus_root)
    docs = loader.load_documents(version="16")

    assert len(docs) == 2
    urls = sorted(item.source_url for item in docs)
    assert urls[0] == "https://www.postgresql.org/docs/16/index.html"
    assert urls[1] == "https://www.postgresql.org/docs/16/sql/select.html"


def test_official_loader_honors_max_pages(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    for idx in range(5):
        _write(corpus_root / "17" / f"p{idx}.html", f"<html><body>{idx}</body></html>")

    loader = OfficialDocumentationLoader(corpus_root=corpus_root)
    docs = loader.load_documents(version="17", max_pages=3)

    assert len(docs) == 3


def test_official_loader_prioritizes_logical_replication_pages_when_limited(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    _write(corpus_root / "16" / "app-pgdump.html", "<html><body><h1>pg_dump</h1></body></html>")
    _write(corpus_root / "16" / "logical-replication.html", "<html><body><h1>Logical Replication</h1></body></html>")
    _write(corpus_root / "16" / "sql-alterpublication.html", "<html><body><h1>ALTER PUBLICATION</h1></body></html>")

    loader = OfficialDocumentationLoader(corpus_root=corpus_root)
    docs = loader.load_documents(version="16", max_pages=1)

    assert len(docs) == 1
    assert docs[0].source_url.endswith("/logical-replication.html") or docs[0].source_url.endswith("/sql-alterpublication.html")
