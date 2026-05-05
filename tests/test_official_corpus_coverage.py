from pathlib import Path

from scripts.validate_official_corpus_coverage import (
    BACKUP_ANY_OF,
    COMMON_REQUIRED_PAGES,
    LOGICAL_REPLICATION_RECOMMENDED,
    MONITORING_RECOMMENDED,
    SUPPORTED_VERSIONS,
    validate_corpus,
)


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<html><body>ok</body></html>", encoding="utf-8")


def create_complete_corpus(root: Path) -> None:
    for version in SUPPORTED_VERSIONS:
        version_dir = root / version

        for page in COMMON_REQUIRED_PAGES:
            touch(version_dir / page)

        touch(version_dir / f"release-{version}.html")
        touch(version_dir / BACKUP_ANY_OF[0])

        for page in LOGICAL_REPLICATION_RECOMMENDED:
            touch(version_dir / page)

        for page in MONITORING_RECOMMENDED:
            touch(version_dir / page)


def test_validate_corpus_accepts_complete_corpus(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    create_complete_corpus(corpus_root)

    errors, stats = validate_corpus(corpus_root)

    assert errors == []
    expected_count = (
        len(COMMON_REQUIRED_PAGES)
        + 1  # release-{version}.html
        + 1  # one page from BACKUP_ANY_OF
        + len(LOGICAL_REPLICATION_RECOMMENDED)
        + len(MONITORING_RECOMMENDED)
    )
    assert stats == {"16": expected_count, "17": expected_count, "18": expected_count}


def test_validate_corpus_reports_missing_required_page(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    create_complete_corpus(corpus_root)

    (corpus_root / "16" / "logical-replication.html").unlink()

    errors, _ = validate_corpus(corpus_root)

    assert any("logical-replication.html" in error for error in errors)


def test_validate_corpus_reports_missing_backup_pages(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus" / "postgres" / "html"
    create_complete_corpus(corpus_root)

    for page in BACKUP_ANY_OF:
        path = corpus_root / "17" / page
        if path.exists():
            path.unlink()

    errors, _ = validate_corpus(corpus_root)

    assert any("Missing backup documentation for PostgreSQL 17" in error for error in errors)
