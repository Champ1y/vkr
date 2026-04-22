from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class RawWebDocument:
    source_url: str
    html: str


class OfficialDocumentationLoader:
    def __init__(self, *, corpus_root: Path | None = None) -> None:
        self.corpus_root = corpus_root or (settings.corpus_path / "postgres" / "html")

    @staticmethod
    def build_base_url(version: str) -> str:
        return f"{settings.official_docs_base_url.rstrip('/')}/{version}/"

    def load_documents(self, *, version: str, max_pages: int | None = None) -> list[RawWebDocument]:
        page_limit = max_pages
        version_dir = self.corpus_root / version
        if not version_dir.exists():
            logger.warning("Official corpus directory not found for version=%s (%s)", version, version_dir)
            return []

        files = sorted(
            [path for path in version_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".htm"}]
        )
        if page_limit is not None:
            files = self._select_priority_subset(files=files, version_dir=version_dir, limit=page_limit)

        base_url = self.build_base_url(version)
        documents: list[RawWebDocument] = []
        for path in files:
            rel = path.relative_to(version_dir).as_posix()
            source_url = urljoin(base_url, rel)
            html = path.read_text(encoding="utf-8", errors="ignore")
            documents.append(RawWebDocument(source_url=source_url, html=html))

        logger.info(
            "Loaded %s local official pages for version=%s from %s",
            len(documents),
            version,
            version_dir,
        )
        return documents

    @staticmethod
    def _select_priority_subset(*, files: list[Path], version_dir: Path, limit: int) -> list[Path]:
        if limit <= 0:
            return []
        if limit >= len(files):
            return files

        priority_markers = (
            "logical-replication",
            "logicaldecoding",
            "runtime-config-replication",
            "sql-createpublication",
            "sql-alterpublication",
            "sql-createsubscription",
            "sql-altersubscription",
            "pg_createsubscriber",
            "app-pgcreatesubscriber",
            "release-",
            "warm-standby",
            "high-availability",
            "index.html",
        )

        def score(path: Path) -> tuple[int, str]:
            rel = path.relative_to(version_dir).as_posix().lower()
            priority = 0
            if any(marker in rel for marker in priority_markers):
                priority += 5
            if rel.startswith("logical-") or rel.startswith("runtime-config-"):
                priority += 2
            if rel.startswith("app-"):
                priority -= 1
            return priority, rel

        ranked = sorted(files, key=score, reverse=True)
        return ranked[:limit]
