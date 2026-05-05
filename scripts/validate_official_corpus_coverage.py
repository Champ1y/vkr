#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_ROOT = PROJECT_ROOT / "corpus" / "postgres" / "html"

SUPPORTED_VERSIONS = ("16", "17", "18")

COMMON_REQUIRED_PAGES = (
    "index.html",
    "logical-replication.html",
    "logical-replication-config.html",
    "logical-replication-monitoring.html",
    "runtime-config.html",
    "runtime-config-replication.html",
    "sql-createpublication.html",
    "sql-createsubscription.html",
    "sql-alterpublication.html",
    "sql-altersubscription.html",
    "high-availability.html",
    "monitoring.html",
)

BACKUP_ANY_OF = (
    "backup.html",
    "backup-dump.html",
    "backup-file.html",
    "app-pgbasebackup.html",
    "app-pgverifybackup.html",
    "backup-manifest-format.html",
)

LOGICAL_REPLICATION_RECOMMENDED = (
    "logical-replication-publication.html",
    "logical-replication-subscription.html",
    "logical-replication-quick-setup.html",
    "logical-replication-restrictions.html",
)

MONITORING_RECOMMENDED = (
    "monitoring-stats.html",
    "monitoring-locks.html",
)


def validate_version(version_dir: Path, version: str) -> list[str]:
    errors: list[str] = []

    if not version_dir.exists():
        return [f"Missing version directory: {version_dir}"]

    required_pages = list(COMMON_REQUIRED_PAGES)
    required_pages.append(f"release-{version}.html")

    for page in required_pages:
        path = version_dir / page
        if not path.is_file():
            errors.append(f"Missing required page for PostgreSQL {version}: {path}")

    if not any((version_dir / page).is_file() for page in BACKUP_ANY_OF):
        expected = ", ".join(BACKUP_ANY_OF)
        errors.append(
            f"Missing backup documentation for PostgreSQL {version}: expected at least one of [{expected}]"
        )

    for page in LOGICAL_REPLICATION_RECOMMENDED:
        path = version_dir / page
        if not path.is_file():
            errors.append(f"Missing recommended logical replication page for PostgreSQL {version}: {path}")

    for page in MONITORING_RECOMMENDED:
        path = version_dir / page
        if not path.is_file():
            errors.append(f"Missing recommended monitoring page for PostgreSQL {version}: {path}")

    return errors


def validate_corpus(corpus_root: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats: dict[str, int] = {}

    for version in SUPPORTED_VERSIONS:
        version_dir = corpus_root / version
        errors.extend(validate_version(version_dir, version))
        stats[version] = len(list(version_dir.glob("*.html"))) if version_dir.exists() else 0

    return errors, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required PostgreSQL official documentation pages in local corpus."
    )
    parser.add_argument(
        "--corpus-root",
        default=str(DEFAULT_CORPUS_ROOT),
        help="Path to corpus/postgres/html directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus_root = Path(args.corpus_root).resolve()

    errors, stats = validate_corpus(corpus_root)

    if errors:
        print("ERROR: official corpus coverage validation failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK: official corpus coverage is valid")
    print(f"Corpus root: {corpus_root}")
    for version in SUPPORTED_VERSIONS:
        print(f"PostgreSQL {version}: {stats[version]} HTML pages checked")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
