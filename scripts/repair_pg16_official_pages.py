from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]

VERSION = "16"
BASE_DIR = ROOT / "corpus" / "postgres" / "html" / VERSION
MANIFEST_PATH = BASE_DIR / "download_manifest.jsonl"

PAGES = [
    "bloom.html",
    "pgvisibility.html",
    "release-16-5.html",
    "docguide-docbook.html",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def download_page(filename: str) -> dict:
    url = f"https://www.postgresql.org/docs/{VERSION}/{filename}"
    local_path = BASE_DIR / filename

    response = requests.get(
        url,
        timeout=60,
        headers={
            "User-Agent": "PostgreSQL-RAG-VKR-Corpus-Repair/1.0"
        },
    )

    response.raise_for_status()

    text = response.text

    # Минимальная проверка, что это действительно HTML-документация PostgreSQL
    if "<html" not in text.lower() or "PostgreSQL" not in text:
        raise RuntimeError(f"Downloaded content for {filename} does not look like PostgreSQL HTML docs")

    local_path.write_text(text, encoding="utf-8")

    return {
        "version": VERSION,
        "pg_major_version": VERSION,
        "corpus_type": "official",
        "language": "en",
        "source_url": url,
        "local_path": str(Path("corpus") / "postgres" / "html" / VERSION / filename),
        "status": "downloaded",
        "http_status": response.status_code,
        "content_hash": f"sha256:{sha256_text(text)}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "license": "PostgreSQL License",
    }


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []

    rows = []
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_manifest(rows: list[dict]) -> None:
    backup = MANIFEST_PATH.with_suffix(".jsonl.bak")
    if MANIFEST_PATH.exists():
        backup.write_text(MANIFEST_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    rows = load_manifest()
    by_filename = {}

    for i, row in enumerate(rows):
        local_path = str(row.get("local_path", ""))
        source_url = str(row.get("source_url", ""))
        name = Path(local_path).name or Path(source_url).name
        if name:
            by_filename[name] = i

    repaired = []

    for filename in PAGES:
        print(f"Downloading {filename}...")
        row = download_page(filename)
        repaired.append(filename)

        if filename in by_filename:
            rows[by_filename[filename]] = row
        else:
            rows.append(row)

    save_manifest(rows)

    print()
    print("Repaired pages:")
    for filename in repaired:
        print(f"  - {filename}")

    print()
    print(f"Updated manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
