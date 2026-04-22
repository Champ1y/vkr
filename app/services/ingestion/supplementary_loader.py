from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class RawSupplementaryDocument:
    source_url: str
    title: str
    text: str
    raw_content: str


class SupplementaryCorpusLoader:
    def __init__(self, *, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or settings.supplementary_path

    def load_documents(self, *, version: str) -> list[RawSupplementaryDocument]:
        version_dir = self.root_dir / version
        if not version_dir.exists():
            logger.info("No supplementary corpus directory for version=%s (%s)", version, version_dir)
            return []

        docs: list[RawSupplementaryDocument] = []
        for path in sorted(version_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt", ".html", ".htm"}:
                continue

            raw_content = path.read_text(encoding="utf-8", errors="ignore")
            title, text = self._extract_text(path, raw_content)
            if len(text.strip()) < 20:
                continue

            rel = path.relative_to(version_dir).as_posix()
            source_url = f"supplementary://{version}/{rel}"
            docs.append(
                RawSupplementaryDocument(
                    source_url=source_url,
                    title=title,
                    text=text,
                    raw_content=raw_content,
                )
            )

        logger.info("Loaded %s supplementary docs for version=%s", len(docs), version)
        return docs

    @staticmethod
    def _extract_text(path: Path, raw_content: str) -> tuple[str, str]:
        suffix = path.suffix.lower()
        if suffix in {".html", ".htm"}:
            soup = BeautifulSoup(raw_content, "lxml")
            title = (soup.select_one("h1") or soup.select_one("title"))
            title_text = title.get_text(strip=True) if title else path.stem
            body = soup.select_one("main") or soup.body or soup
            text = body.get_text("\n", strip=True)
            return title_text, text

        lines = [line.strip() for line in raw_content.splitlines()]
        title = next((line.lstrip("# ") for line in lines if line), path.stem)
        text = "\n".join(line for line in lines if line)
        return title, text
