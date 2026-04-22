from __future__ import annotations

import argparse

from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.repositories.versions import VersionRepository
from app.services.ingestion.indexer import IndexingPipeline


configure_logging()


def cmd_seed_versions(versions: list[str] | None) -> None:
    with SessionLocal() as db:
        rows = VersionRepository(db).ensure_seed_versions(versions)
        print(f"Seeded/updated versions: {', '.join(row.major_version for row in rows)}")


def cmd_reindex(versions: list[str], include_official: bool, include_supplementary: bool, max_pages: int | None) -> None:
    with SessionLocal() as db:
        pipeline = IndexingPipeline(db)
        for version in versions:
            stats = pipeline.reindex_version(
                version=version,
                include_official=include_official,
                include_supplementary=include_supplementary,
                max_pages=max_pages,
            )
            print(
                f"v{stats.version}: official_docs={stats.official_documents}; "
                f"supplementary_docs={stats.supplementary_documents}; chunks={stats.indexed_chunks}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RAG PostgreSQL project management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_cmd = subparsers.add_parser("seed-versions", help="Seed supported PostgreSQL versions")
    seed_cmd.add_argument("--versions", nargs="*", help="Optional list of major versions")

    reindex_cmd = subparsers.add_parser("reindex", help="Reindex corpus by versions")
    reindex_cmd.add_argument("--versions", nargs="+", required=True, help="Major versions, e.g. 16 17")
    reindex_cmd.add_argument("--official", action="store_true", help="Reindex official corpus")
    reindex_cmd.add_argument("--supplementary", action="store_true", help="Reindex supplementary corpus")
    reindex_cmd.add_argument("--max-pages", type=int, default=None, help="Max official pages to crawl")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "seed-versions":
        cmd_seed_versions(args.versions)
        return

    if args.command == "reindex":
        include_official = args.official or not args.supplementary
        include_supplementary = args.supplementary
        cmd_reindex(
            versions=args.versions,
            include_official=include_official,
            include_supplementary=include_supplementary,
            max_pages=args.max_pages,
        )


if __name__ == "__main__":
    main()
