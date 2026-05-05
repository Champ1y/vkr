#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


VERSION_BASE = {
    "16": "https://www.postgresql.org/docs/16/",
    "17": "https://www.postgresql.org/docs/17/",
    "18": "https://www.postgresql.org/docs/18/",
}

RELEASE_PAGE = {
    "16": "release-16.html",
    "17": "release-17.html",
    "18": "release-18.html",
}

USER_AGENT = "RAG-Postgres-Corpus-Filler/1.0 (+student project)"
TIMEOUT = 30
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def normalize_url(url: str) -> str:
    clean, _ = urldefrag(url)
    return clean


def version_prefix(version: str) -> str:
    return f"/docs/{version}/"


def normalize_postgres_docs_url(source_url: str, pg_version: str) -> str:
    return (
        source_url.replace(
            "https://www.postgresql.org/docs/current/",
            f"https://www.postgresql.org/docs/{pg_version}/",
        ).replace("/docs/current/", f"/docs/{pg_version}/")
    )


def is_same_version_html(url: str, version: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc != "www.postgresql.org":
        return False

    path = parsed.path
    if not path.startswith(version_prefix(version)):
        return False

    # Берем только HTML/manual pages
    if path.endswith("/"):
        return True
    if path.endswith(".html"):
        return True
    return False


def remote_to_local(url: str, version: str, root: Path) -> Path:
    parsed = urlparse(url)
    path = parsed.path
    prefix = version_prefix(version)

    rel = path[len(prefix):]
    if not rel or rel.endswith("/"):
        rel = rel + "index.html"

    return root / version / rel


def local_to_remote(local_file: Path, version: str, version_root: Path) -> str:
    rel = local_file.relative_to(version_root).as_posix()
    return urljoin(VERSION_BASE[version], rel)


def extract_links(html: str, page_url: str, version: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = normalize_url(urljoin(page_url, tag["href"]))
        if is_same_version_html(href, version):
            links.add(href)

    return links


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def manifest_local_path(local_path: Path) -> str:
    """Store local_path in manifest relative to repository root when possible."""
    try:
        return local_path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return local_path.as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def fetch(session: requests.Session, url: str) -> str:
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def seed_urls_from_local(version_root: Path, version: str) -> set[str]:
    urls = set()

    if not version_root.exists():
        return urls

    for file in version_root.rglob("*.html"):
        urls.add(local_to_remote(file, version, version_root))

    # Гарантируем major release page
    urls.add(urljoin(VERSION_BASE[version], RELEASE_PAGE[version]))
    return urls


def crawl_and_fill(root: Path, version: str, delay: float) -> None:
    version_root = root / version
    version_root.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    queue = deque(sorted(seed_urls_from_local(version_root, version)))
    seen: set[str] = set()
    manifest_path = version_root / "download_manifest.jsonl"

    print(f"\n=== VERSION {version} ===")
    print(f"Local root: {version_root}")
    print(f"Seed URLs: {len(queue)}")

    with manifest_path.open("a", encoding="utf-8") as manifest:
        while queue:
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)

            local_path = remote_to_local(url, version, root)

            try:
                if local_path.exists():
                    html = read_text(local_path)
                    status = "existing"
                    print(f"[EXISTS] {local_path.relative_to(root)}")
                else:
                    print(f"[GET]    {url}")
                    html = fetch(session, url)
                    ensure_parent(local_path)
                    local_path.write_text(html, encoding="utf-8")
                    status = "downloaded"
                    time.sleep(delay)

                record = {
                    "version": version,
                    "source_url": normalize_postgres_docs_url(url, version),
                    "local_path": manifest_local_path(local_path),
                    "status": status,
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

                for link in extract_links(html, url, version):
                    if link not in seen:
                        queue.append(link)

            except requests.HTTPError as e:
                print(f"[HTTP {e.response.status_code}] {url}", file=sys.stderr)
                record = {
                    "version": version,
                    "source_url": normalize_postgres_docs_url(url, version),
                    "local_path": manifest_local_path(local_path),
                    "status": "http_error",
                    "error": str(e),
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

            except Exception as e:
                print(f"[ERROR] {url} -> {e}", file=sys.stderr)
                record = {
                    "version": version,
                    "source_url": normalize_postgres_docs_url(url, version),
                    "local_path": manifest_local_path(local_path),
                    "status": "error",
                    "error": str(e),
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Manifest written to: {manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill missing PostgreSQL docs HTML pages for local corpus."
    )
    parser.add_argument(
        "--root",
        default="/home/arz/Desktop/RAG_postgres/corpus/postgres/html",
        help="Root directory containing 16/17/18 folders",
    )
    parser.add_argument(
        "--versions",
        nargs="*",
        default=["16", "17", "18"],
        choices=["16", "17", "18"],
        help="Versions to process",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Delay between remote requests in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_root = Path(args.root)
    root = raw_root if raw_root.is_absolute() else (PROJECT_ROOT / raw_root)
    root = root.resolve()

    for version in args.versions:
        crawl_and_fill(root=root, version=version, delay=args.delay)


if __name__ == "__main__":
    main()
