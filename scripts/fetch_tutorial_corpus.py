#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


USER_AGENT = "RAG-Postgres-Tutorial-Corpus/1.0 (+student project)"
TIMEOUT = 30

SOURCES = [
    {
        "name": "postgres_wiki_main",
        "seeds": [
            "https://wiki.postgresql.org/wiki/Main_Page",
        ],
        "allowed_prefixes": [
            "https://wiki.postgresql.org/wiki/",
        ],
        "max_pages": 80,
    },
    {
        "name": "postgres_wiki_faq",
        "seeds": [
            "https://wiki.postgresql.org/wiki/FAQ",
        ],
        "allowed_prefixes": [
            "https://wiki.postgresql.org/wiki/",
        ],
        "max_pages": 120,
    },
    {
        "name": "postgres_wiki_install_guides",
        "seeds": [
            "https://wiki.postgresql.org/wiki/Detailed_installation_guides",
        ],
        "allowed_prefixes": [
            "https://wiki.postgresql.org/wiki/",
        ],
        "max_pages": 120,
    },
    {
        "name": "postgresql_tutorial_neon",
        "seeds": [
            "https://neon.com/postgresql/tutorial",
        ],
        "allowed_prefixes": [
            "https://neon.com/postgresql/tutorial",
        ],
        "max_pages": 250,
    },
    {
        "name": "pgexercises",
        "seeds": [
            "https://pgexercises.com/",
            "https://pgexercises.com/gettingstarted.html",
            "https://pgexercises.com/questions/basic/",
            "https://pgexercises.com/questions/joins/",
            "https://pgexercises.com/questions/aggregates/",
            "https://pgexercises.com/questions/date/",
            "https://pgexercises.com/questions/string/",
            "https://pgexercises.com/questions/recursive/",
        ],
        "allowed_prefixes": [
            "https://pgexercises.com/",
        ],
        "max_pages": 300,
    },
]

# Опционально можно вручную включить pgPedia, когда зафиксируешь канонический домен.
# Например:
#
# OPTIONAL_SOURCES = [
#     {
#         "name": "pgpedia",
#         "seeds": [
#             "https://pgpedia.com/",
#         ],
#         "allowed_prefixes": [
#             "https://pgpedia.com/",
#         ],
#         "max_pages": 250,
#     }
# ]


def normalize_url(url: str) -> str:
    clean, _ = urldefrag(url)
    return clean.strip()


def is_html_like(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()

    if path.endswith((
        ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".ico", ".pdf", ".zip", ".gz", ".tar", ".bz2", ".xml", ".json",
        ".mp4", ".mp3", ".woff", ".woff2", ".ttf", ".eot"
    )):
        return False

    return parsed.scheme in {"http", "https"}


def url_allowed(url: str, allowed_prefixes: list[str]) -> bool:
    return any(url.startswith(prefix) for prefix in allowed_prefixes)


def extract_links(html: str, page_url: str, allowed_prefixes: list[str]) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = normalize_url(urljoin(page_url, a["href"]))
        if is_html_like(href) and url_allowed(href, allowed_prefixes):
            out.add(href)

    return out


def url_to_local_path(url: str, source_dir: Path) -> Path:
    parsed = urlparse(url)
    path = parsed.path

    if not path or path.endswith("/"):
        path = path + "index.html"
    elif "." not in Path(path).name:
        path = path + ".html"

    local = source_dir / path.lstrip("/")
    local.parent.mkdir(parents=True, exist_ok=True)
    return local


def fetch_html(session: requests.Session, url: str) -> str:
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def crawl_source(base_out: Path, source_cfg: dict, delay: float) -> None:
    name = source_cfg["name"]
    seeds = source_cfg["seeds"]
    allowed_prefixes = source_cfg["allowed_prefixes"]
    max_pages = source_cfg["max_pages"]

    source_dir = base_out / name
    source_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = source_dir / "manifest.jsonl"

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    queue = deque(seeds)
    seen: set[str] = set()
    saved = 0

    print(f"\n=== {name} ===")
    print(f"Output: {source_dir}")
    print(f"Seeds: {len(seeds)} | Max pages: {max_pages}")

    with manifest_path.open("a", encoding="utf-8") as manifest:
        while queue and saved < max_pages:
            url = normalize_url(queue.popleft())

            if url in seen:
                continue
            seen.add(url)

            if not is_html_like(url) or not url_allowed(url, allowed_prefixes):
                continue

            local_path = url_to_local_path(url, source_dir)

            try:
                if local_path.exists():
                    html = local_path.read_text(encoding="utf-8", errors="ignore")
                    status = "existing"
                    print(f"[EXISTS] {local_path.relative_to(base_out)}")
                else:
                    print(f"[GET]    {url}")
                    html = fetch_html(session, url)
                    local_path.write_text(html, encoding="utf-8")
                    status = "downloaded"
                    time.sleep(delay)

                record = {
                    "source_name": name,
                    "source_url": url,
                    "local_path": str(local_path),
                    "status": status,
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
                saved += 1

                for link in extract_links(html, url, allowed_prefixes):
                    if link not in seen:
                        queue.append(link)

            except requests.HTTPError as e:
                print(f"[HTTP {e.response.status_code}] {url}")
                record = {
                    "source_name": name,
                    "source_url": url,
                    "local_path": str(local_path),
                    "status": "http_error",
                    "error": str(e),
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

            except Exception as e:
                print(f"[ERROR] {url} -> {e}")
                record = {
                    "source_name": name,
                    "source_url": url,
                    "local_path": str(local_path),
                    "status": "error",
                    "error": str(e),
                }
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved pages: {saved}")
    print(f"Manifest: {manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download supplementary tutorial corpus sources into local HTML folders."
    )
    parser.add_argument(
        "--root",
        default="corpus/tutorial/html",
        help="Output root directory for tutorial corpus HTML",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        default=[src["name"] for src in SOURCES],
        help="Subset of sources to download",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_out = Path(args.root)
    base_out.mkdir(parents=True, exist_ok=True)

    source_map = {src["name"]: src for src in SOURCES}

    for source_name in args.sources:
        if source_name not in source_map:
            print(f"[WARN] Unknown source: {source_name}")
            continue
        crawl_source(base_out, source_map[source_name], args.delay)


if __name__ == "__main__":
    main()