#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HTML_ROOT = PROJECT_ROOT / "corpus" / "postgres" / "html"
SUPPORTED_VERSIONS = ("16", "17", "18")
LICENSE_NAME = "PostgreSQL License"
LICENSE_URL = "https://www.postgresql.org/about/licence/"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_local_path(path_value: str) -> str:
    raw = Path(str(path_value).strip())
    if raw.is_absolute():
        try:
            return raw.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            return raw.as_posix()
    return raw.as_posix()


def normalize_source_url(url: str, version: str) -> str:
    return (
        str(url).strip()
        .replace("https://www.postgresql.org/docs/current/", f"https://www.postgresql.org/docs/{version}/")
        .replace("/docs/current/", f"/docs/{version}/")
    )


def source_url_from_local(html_file: Path, version: str, version_root: Path) -> str:
    rel = html_file.relative_to(version_root).as_posix()
    return f"https://www.postgresql.org/docs/{version}/{rel}"


def extract_title(html_path: Path) -> str:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")

    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(" ", strip=True)
        if text:
            return text

    title = soup.find("title")
    if title:
        text = title.get_text(" ", strip=True)
        if text:
            return text

    return html_path.name


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def load_old_manifest(manifest_path: Path, version: str) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_local: dict[str, dict[str, Any]] = {}
    by_source: dict[str, dict[str, Any]] = {}

    if not manifest_path.exists():
        return by_local, by_source

    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            print(f"[WARN] Skip invalid JSON in {manifest_path}:{line_no}")
            continue

        local_path = row.get("local_path")
        if isinstance(local_path, str) and local_path.strip():
            by_local[normalize_local_path(local_path)] = row

        source_url = row.get("source_url")
        if isinstance(source_url, str) and source_url.strip():
            by_source[normalize_source_url(source_url, version)] = row

    return by_local, by_source


def backup_manifest(manifest_path: Path) -> Path | None:
    if not manifest_path.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = manifest_path.with_name(f"{manifest_path.name}.bak.{ts}")
    manifest_path.replace(backup_path)
    return backup_path


def enrich_version(version: str, manifest_updated_at: str) -> tuple[int, Path]:
    version_root = OFFICIAL_HTML_ROOT / version
    if not version_root.exists():
        raise FileNotFoundError(f"Version folder not found: {version_root}")

    manifest_path = version_root / "download_manifest.jsonl"
    by_local, by_source = load_old_manifest(manifest_path, version)
    backup_path = backup_manifest(manifest_path)

    html_files = sorted(
        p for p in version_root.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}
    )

    rows: list[dict[str, Any]] = []
    for html_file in html_files:
        local_path = html_file.resolve().relative_to(PROJECT_ROOT).as_posix()
        source_url = source_url_from_local(html_file, version, version_root)

        old_row = by_local.get(local_path) or by_source.get(source_url)
        status = (old_row or {}).get("status", "existing")
        http_status = (old_row or {}).get("http_status", None)
        downloaded_at = (old_row or {}).get("downloaded_at", None)

        row = {
            "corpus_type": "official",
            "pg_major_version": version,
            "language": "en",
            "source_url": source_url,
            "local_path": local_path,
            "title": extract_title(html_file),
            "status": status,
            "http_status": http_status,
            "content_hash": sha256_file(html_file),
            "downloaded_at": downloaded_at,
            "manifest_updated_at": manifest_updated_at,
            "license": LICENSE_NAME,
            "license_url": LICENSE_URL,
        }
        rows.append(row)

    with manifest_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    if backup_path:
        print(f"[{version}] Backup: {backup_path}")
    else:
        print(f"[{version}] Backup: not needed (manifest did not exist)")
    print(f"[{version}] Rewritten rows: {len(rows)} -> {manifest_path}")
    return len(rows), manifest_path


def main() -> None:
    manifest_updated_at = now_utc_iso()
    total_rows = 0

    for version in SUPPORTED_VERSIONS:
        rows, _ = enrich_version(version, manifest_updated_at)
        total_rows += rows

    print(f"Done. Updated official manifests: {len(SUPPORTED_VERSIONS)}")
    print(f"Total rows written: {total_rows}")
    print(f"manifest_updated_at: {manifest_updated_at}")


if __name__ == "__main__":
    main()
