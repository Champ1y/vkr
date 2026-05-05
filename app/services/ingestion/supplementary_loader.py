from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    _LEGACY_SUFFIX = ("data", "supplementary")

    def __init__(self, *, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or settings.supplementary_path

    def load_documents(self, *, version: str) -> list[RawSupplementaryDocument]:
        if self._is_legacy_layout():
            return self._load_legacy_documents(version=version)
        return self._load_tutorial_documents(version=version)

    def _load_tutorial_documents(self, *, version: str) -> list[RawSupplementaryDocument]:
        curated_root = self.root_dir / "curated" / version
        processed_root = self.root_dir / "processed_html"
        if not curated_root.exists() and not processed_root.exists():
            logger.info(
                "No tutorial supplementary corpus for version=%s under %s (expected curated/%s and processed_html/).",
                version,
                self.root_dir,
                version,
            )
            return []

        curated_docs = self._load_curated_documents(version=version, curated_root=curated_root)
        processed_docs = self._load_processed_html_documents(processed_root=processed_root)
        docs = curated_docs + processed_docs

        logger.info(
            "Loaded %s supplementary docs for version=%s (curated=%s, processed_html=%s, root=%s)",
            len(docs),
            version,
            len(curated_docs),
            len(processed_docs),
            self.root_dir,
        )
        return docs

    def _load_curated_documents(self, *, version: str, curated_root: Path) -> list[RawSupplementaryDocument]:
        if not curated_root.exists():
            logger.info("Curated supplementary directory not found for version=%s (%s)", version, curated_root)
            return []

        docs: list[RawSupplementaryDocument] = []
        for path in sorted(curated_root.rglob("*.md")):
            if self._should_skip_path(path):
                continue

            raw_content = path.read_text(encoding="utf-8", errors="ignore")
            metadata, body, has_front_matter = self._parse_markdown_with_front_matter(raw_content)
            if not has_front_matter:
                logger.warning("Curated file has no YAML front matter: %s", path)

            pg_version = str(metadata.get("pg_version", "")).strip()
            if pg_version and pg_version != version:
                logger.warning("Skip curated doc with mismatched pg_version: %s (pg_version=%s, target=%s)", path, pg_version, version)
                continue

            text = body.strip()
            if len(text) < 20:
                continue

            rel = path.relative_to(curated_root).as_posix()
            source_url = f"supplementary://curated/{version}/{rel}"
            docs.append(
                RawSupplementaryDocument(
                    source_url=source_url,
                    title=self._resolve_title(metadata=metadata, body=body, path=path),
                    text=text,
                    raw_content=raw_content,
                )
            )

        return docs

    def _load_processed_html_documents(self, *, processed_root: Path) -> list[RawSupplementaryDocument]:
        if not processed_root.exists():
            logger.info("processed_html directory not found under supplementary root (%s)", processed_root)
            return []

        docs: list[RawSupplementaryDocument] = []
        for path in sorted(processed_root.rglob("*.md")):
            if self._should_skip_path(path):
                continue

            raw_content = path.read_text(encoding="utf-8", errors="ignore")
            metadata, body, has_front_matter = self._parse_markdown_with_front_matter(raw_content)
            if not has_front_matter:
                logger.warning("processed_html file has no YAML front matter: %s", path)
                continue

            if not self._as_bool(metadata.get("indexable"), default=False):
                continue

            source_url = str(metadata.get("source_url", "")).strip()
            if not source_url:
                logger.warning("Skip processed_html doc without source_url metadata: %s", path)
                continue

            text = body.strip()
            if len(text) < 20:
                continue

            docs.append(
                RawSupplementaryDocument(
                    source_url=source_url,
                    title=self._resolve_title(metadata=metadata, body=body, path=path),
                    text=text,
                    raw_content=raw_content,
                )
            )

        return docs

    def _load_legacy_documents(self, *, version: str) -> list[RawSupplementaryDocument]:
        version_dir = self.root_dir / version
        if not version_dir.exists():
            logger.info("No legacy supplementary corpus directory for version=%s (%s)", version, version_dir)
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

        logger.info("Loaded %s legacy supplementary docs for version=%s root=%s", len(docs), version, self.root_dir)
        return docs

    def _is_legacy_layout(self) -> bool:
        parts = self.root_dir.as_posix().strip("/").split("/")
        return tuple(parts[-2:]) == self._LEGACY_SUFFIX

    @staticmethod
    def _should_skip_path(path: Path) -> bool:
        upper_name = path.name.upper()
        if "REPORT" in upper_name or "MANIFEST" in upper_name:
            return True
        if path.suffix.lower() in {".pyc", ".bak"}:
            return True
        if any(part == "__pycache__" for part in path.parts):
            return True
        if any(part.startswith("_backup") for part in path.parts):
            return True
        return False

    @staticmethod
    def _parse_markdown_with_front_matter(raw_content: str) -> tuple[dict[str, Any], str, bool]:
        if not raw_content.startswith("---"):
            return {}, raw_content, False

        lines = raw_content.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, raw_content, False

        end_index = None
        for idx, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_index = idx
                break
        if end_index is None:
            return {}, raw_content, False

        fm_lines = lines[1:end_index]
        body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
        metadata: dict[str, Any] = {}
        current_key: str | None = None

        for raw_line in fm_lines:
            line = raw_line.rstrip()
            if not line.strip():
                continue

            if line.startswith("  - ") and current_key:
                value = SupplementaryCorpusLoader._strip_quotes(line[4:].strip())
                existing = metadata.get(current_key)
                if isinstance(existing, list):
                    existing.append(value)
                else:
                    metadata[current_key] = [value]
                continue

            if ":" in line and not line.startswith(" "):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value == "":
                    metadata[key] = []
                    current_key = key
                else:
                    metadata[key] = SupplementaryCorpusLoader._parse_scalar(value)
                    current_key = key

        return metadata, body, True

    @staticmethod
    def _strip_quotes(value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] and trimmed[0] in {'"', "'"}:
            return trimmed[1:-1]
        return trimmed

    @staticmethod
    def _parse_scalar(value: str) -> Any:
        normalized = SupplementaryCorpusLoader._strip_quotes(value)
        lowered = normalized.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "none"}:
            return None
        return normalized

    @staticmethod
    def _as_bool(value: Any, *, default: bool) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes"}:
                return True
            if lowered in {"false", "0", "no"}:
                return False
        return default

    @staticmethod
    def _resolve_title(*, metadata: dict[str, Any], body: str, path: Path) -> str:
        title = str(metadata.get("title", "")).strip()
        if title:
            return title
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                candidate = stripped.lstrip("#").strip()
                if candidate:
                    return candidate
        return path.stem

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
