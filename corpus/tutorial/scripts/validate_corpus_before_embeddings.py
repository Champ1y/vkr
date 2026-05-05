#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strict corpus validator and QUALITY_REPORT updater.

Назначение:
- Исправляет проблему ложноположительного QUALITY_REPORT / validator.
- Проверяет corpus перед пересчётом chunks и embeddings.
- Обновляет corpus/tutorial/QUALITY_REPORT.json реальными ошибками.
- Создаёт corpus/CORPUS_FINAL_AUDIT_REPORT.md.
- Устанавливает этот же валидатор в corpus/tutorial/scripts/validate_corpus_before_embeddings.py.

Запуск:
python3 ~/Desktop/scripts/audit_and_update_corpus_quality.py --corpus-root /home/arz/Desktop/RAG_postgres/corpus
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSIONS = ["16", "17", "18"]

FORBIDDEN_CURATED_STRINGS = [
    "view-pg-stat-activity.html",
    "view-pg-stat-replication.html",
    "view-pg-stat-subscription.html",
    "view-pg-extension.html",
    "streaming-replication.html",
    "https://www.postgresql.org/docs/18/runtime-config-autovacuum.html",
]

REQUIRED_CURATED_META = [
    "title",
    "pg_version",
    "language",
    "corpus_type",
    "source_role",
    "official_backing",
]

REQUIRED_PROCESSED_META = [
    "title",
    "language",
    "corpus_type",
    "source_role",
    "indexable",
    "original_html_path",
    "source_url",
]

PGEX_NAV_WORDS = [
    "PostgreSQL Exercises",
    "Home",
    "Getting Started",
    "Exercises",
    "Basic",
    "Joins and Subqueries",
    "Modifying data",
    "Aggregates",
    "Date",
    "String",
    "Recursive",
    "About",
    "Options",
    "Back to listing",
]

WIKI_JUNK_PATTERNS = [
    "Special:",
    "Category:",
    "Talk:",
    "User:",
    "PostgreSQL_wiki:",
]


@dataclass
class Finding:
    level: str
    code: str
    path: str
    message: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    """
    Минимальный YAML front matter parser без внешних зависимостей.
    Поддерживает:
    key: value
    key:
      - item
      - item
    """
    if not text.startswith("---\n"):
        return {}, text, False

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, False

    fm_raw = parts[1]
    body = parts[2].lstrip("\n")
    meta: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in fm_raw.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        if line.startswith("  - ") and current_key:
            value = line[4:].strip().strip('"').strip("'")
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(value)
            continue

        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value == "":
                meta[key] = []
                current_key = key
            else:
                meta[key] = value.strip('"').strip("'")
                current_key = key
            continue

    return meta, body, True


def dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def count_files(root: Path, pattern: str) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob(pattern) if p.is_file())


def extract_official_urls(meta: dict[str, Any]) -> list[str]:
    value = meta.get("official_backing", [])
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(x) for x in value]
    return []


def official_url_to_local_path(url: str, corpus_root: Path) -> Path | None:
    m = re.match(r"^https://www\.postgresql\.org/docs/(16|17|18)/([^#?]+)$", url)
    if not m:
        return None
    version, page = m.group(1), m.group(2)
    if not page.endswith(".html"):
        return None
    return corpus_root / "postgres" / "html" / version / page


def expected_source_url(original_html_path: str) -> str | None:
    p = original_html_path.strip().strip('"').strip("'")

    if p.startswith("html/pgexercises/"):
        suffix = p.removeprefix("html/pgexercises/")
        return "https://pgexercises.com/" + suffix

    if p.startswith("html/postgres_wiki_whitelist/wiki/"):
        name = Path(p).name
        if name.endswith(".html"):
            name = name[:-5]
        return "https://wiki.postgresql.org/wiki/" + name

    return None


def check_official(corpus_root: Path, findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for version in VERSIONS:
        vdir = corpus_root / "postgres" / "html" / version
        if not vdir.exists():
            findings.append(Finding(
                "ERROR",
                "OFFICIAL_VERSION_DIR_MISSING",
                rel(vdir, corpus_root),
                f"Не найдена папка official docs PostgreSQL {version}",
            ))
            counts[version] = 0
            continue

        html_count = count_files(vdir, "*.html")
        counts[version] = html_count
        if html_count == 0:
            findings.append(Finding(
                "ERROR",
                "OFFICIAL_HTML_EMPTY",
                rel(vdir, corpus_root),
                f"В official docs PostgreSQL {version} нет .html файлов",
            ))

    for bak in (corpus_root / "postgres" / "html").rglob("download_manifest.jsonl.bak*"):
        findings.append(Finding(
            "ERROR",
            "OFFICIAL_BACKUP_FILE_REMAINS",
            rel(bak, corpus_root),
            "В official corpus остался служебный backup-файл download_manifest.jsonl.bak*",
        ))

    return counts


def check_curated(corpus_root: Path, findings: list[Finding]) -> dict[str, Any]:
    curated_root = corpus_root / "tutorial" / "curated"
    md_files = sorted(curated_root.glob("*/*.md")) if curated_root.exists() else []

    broken_official_backing: list[dict[str, str]] = []
    forbidden_hits: list[dict[str, str]] = []

    if not curated_root.exists():
        findings.append(Finding(
            "ERROR",
            "CURATED_ROOT_MISSING",
            rel(curated_root, corpus_root),
            "Не найдена папка corpus/tutorial/curated",
        ))

    for md in md_files:
        text = read_text(md)
        meta, body, has_fm = parse_frontmatter(text)

        if not has_fm:
            findings.append(Finding(
                "ERROR",
                "CURATED_NO_FRONTMATTER",
                rel(md, corpus_root),
                "Curated .md файл не имеет YAML front matter",
            ))
            continue

        for key in REQUIRED_CURATED_META:
            if key not in meta or meta.get(key) in ("", [], None):
                findings.append(Finding(
                    "ERROR",
                    "CURATED_REQUIRED_META_MISSING",
                    rel(md, corpus_root),
                    f"В curated .md отсутствует обязательное metadata-поле: {key}",
                ))

        for forbidden in FORBIDDEN_CURATED_STRINGS:
            if forbidden in text:
                forbidden_hits.append({"file": rel(md, corpus_root), "string": forbidden})
                findings.append(Finding(
                    "ERROR",
                    "CURATED_FORBIDDEN_OLD_BACKING_STRING",
                    rel(md, corpus_root),
                    f"Осталась запрещённая старая official_backing строка: {forbidden}",
                ))

        urls = extract_official_urls(meta)
        for url in urls:
            local = official_url_to_local_path(url, corpus_root)

            if local is None:
                # external official reference: не обязательно ошибка, но в official_backing это опасно
                findings.append(Finding(
                    "ERROR",
                    "CURATED_OFFICIAL_BACKING_NOT_LOCAL_DOCS_URL",
                    rel(md, corpus_root),
                    f"official_backing содержит URL не из локальной ветки /docs/16-18/*.html: {url}. Перенеси в external_official_reference или убери из official_backing.",
                ))
                broken_official_backing.append({
                    "file": rel(md, corpus_root),
                    "url": url,
                    "reason": "not_local_docs_url",
                })
                continue

            if not local.exists():
                findings.append(Finding(
                    "ERROR",
                    "CURATED_OFFICIAL_BACKING_LOCAL_FILE_MISSING",
                    rel(md, corpus_root),
                    f"official_backing указывает на несуществующий локальный файл: {url} -> {rel(local, corpus_root)}",
                ))
                broken_official_backing.append({
                    "file": rel(md, corpus_root),
                    "url": url,
                    "local_path": rel(local, corpus_root),
                    "reason": "local_file_missing",
                })

    return {
        "curated_md_files": len(md_files),
        "broken_official_backing_count": len(broken_official_backing),
        "broken_official_backing": broken_official_backing,
        "forbidden_curated_hits_count": len(forbidden_hits),
        "forbidden_curated_hits": forbidden_hits,
    }


def check_processed_html(corpus_root: Path, findings: list[Finding]) -> dict[str, Any]:
    processed_root = corpus_root / "tutorial" / "processed_html"
    md_files = sorted(processed_root.rglob("*.md")) if processed_root.exists() else []

    missing_source_url = []
    source_url_mismatch = []
    boilerplate_files = []

    if not processed_root.exists():
        findings.append(Finding(
            "ERROR",
            "PROCESSED_HTML_ROOT_MISSING",
            rel(processed_root, corpus_root),
            "Не найдена папка corpus/tutorial/processed_html",
        ))

    for md in md_files:
        text = read_text(md)
        meta, body, has_fm = parse_frontmatter(text)

        if not has_fm:
            findings.append(Finding(
                "ERROR",
                "PROCESSED_NO_FRONTMATTER",
                rel(md, corpus_root),
                "Processed .md файл не имеет YAML front matter",
            ))
            continue

        for key in REQUIRED_PROCESSED_META:
            if key not in meta or meta.get(key) in ("", [], None):
                findings.append(Finding(
                    "ERROR",
                    "PROCESSED_REQUIRED_META_MISSING",
                    rel(md, corpus_root),
                    f"В processed_html .md отсутствует обязательное metadata-поле: {key}",
                ))

        source_url = str(meta.get("source_url", "")).strip()
        original = str(meta.get("original_html_path", "")).strip()

        if not source_url:
            missing_source_url.append(rel(md, corpus_root))
        else:
            expected = expected_source_url(original)
            if expected and source_url != expected:
                source_url_mismatch.append({
                    "file": rel(md, corpus_root),
                    "expected": expected,
                    "actual": source_url,
                })
                findings.append(Finding(
                    "ERROR",
                    "PROCESSED_SOURCE_URL_MISMATCH",
                    rel(md, corpus_root),
                    f"source_url не соответствует original_html_path. expected={expected}, actual={source_url}",
                ))

        # Проверка wiki junk в indexable processed paths
        for junk in WIKI_JUNK_PATTERNS:
            if junk in str(md) or junk in source_url:
                findings.append(Finding(
                    "ERROR",
                    "WIKI_JUNK_IN_PROCESSED_INDEXABLE_PATH",
                    rel(md, corpus_root),
                    f"В indexable processed path/source_url найден wiki junk pattern: {junk}",
                ))

        # Проверка boilerplate PGExercises в начале body
        if "processed_html/pgexercises" in rel(md, corpus_root):
            first_lines = [ln.strip() for ln in body.splitlines()[:40] if ln.strip()]
            first_text = "\n".join(first_lines[:25])
            nav_hits = sum(1 for w in PGEX_NAV_WORDS if w in first_text)

            if nav_hits >= 5:
                boilerplate_files.append(rel(md, corpus_root))
                findings.append(Finding(
                    "ERROR",
                    "PGEXERCISES_NAV_BOILERPLATE_IN_PROCESSED_MD",
                    rel(md, corpus_root),
                    "В начале processed PGExercises .md остался навигационный boilerplate",
                ))

    for f in missing_source_url:
        findings.append(Finding(
            "ERROR",
            "PROCESSED_SOURCE_URL_MISSING",
            f,
            "В processed_html .md отсутствует source_url",
        ))

    return {
        "processed_md_files": len(md_files),
        "missing_source_url_count": len(missing_source_url),
        "missing_source_url": missing_source_url,
        "source_url_mismatch_count": len(source_url_mismatch),
        "source_url_mismatch": source_url_mismatch,
        "pgexercises_boilerplate_count": len(boilerplate_files),
        "pgexercises_boilerplate_files": boilerplate_files,
    }


def check_pgexercises_manifest(corpus_root: Path, findings: list[Finding]) -> dict[str, Any]:
    manifest = corpus_root / "tutorial" / "html" / "pgexercises" / "manifest.jsonl"

    if not manifest.exists():
        findings.append(Finding(
            "WARNING",
            "PGEXERCISES_MANIFEST_MISSING",
            rel(manifest, corpus_root),
            "manifest.jsonl PGExercises не найден",
        ))
        return {
            "pgexercises_manifest_exists": False,
            "error_rows_count": 0,
            "missing_pages_count": 0,
            "error_rows": [],
        }

    error_rows = []
    missing_pages = []
    existing_error_pages = []

    for i, line in enumerate(read_text(manifest).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            findings.append(Finding(
                "ERROR",
                "PGEXERCISES_MANIFEST_BAD_JSONL",
                rel(manifest, corpus_root),
                f"Строка {i} не является валидным JSON",
            ))
            continue

        status = str(obj.get("status", "")).lower()
        if status != "error":
            continue

        url = obj.get("url") or obj.get("source_url") or obj.get("path") or ""
        path = obj.get("path") or obj.get("file") or obj.get("local_path") or ""

        # Пытаемся вывести локальный путь из URL.
        candidates: list[Path] = []
        if path:
            candidates.append(corpus_root / "tutorial" / "html" / "pgexercises" / str(path).lstrip("/"))

        if isinstance(url, str) and "pgexercises.com/" in url:
            suffix = url.split("pgexercises.com/", 1)[1]
            if suffix.endswith("/"):
                suffix = suffix + "index.html"
            candidates.append(corpus_root / "tutorial" / "html" / "pgexercises" / suffix)

        exists = any(c.exists() for c in candidates)

        row = {
            "line": i,
            "url": url,
            "path": path,
            "candidate_paths": [rel(c, corpus_root) for c in candidates],
            "exists": exists,
        }
        error_rows.append(row)

        if exists:
            existing_error_pages.append(row)
            findings.append(Finding(
                "ERROR",
                "PGEXERCISES_MANIFEST_ERROR_BUT_FILE_EXISTS",
                rel(manifest, corpus_root),
                f"manifest содержит status=error, но файл уже существует: {row}",
            ))
        else:
            missing_pages.append(row)
            findings.append(Finding(
                "ERROR",
                "PGEXERCISES_MANIFEST_ERROR_PAGE_MISSING",
                rel(manifest, corpus_root),
                f"manifest содержит status=error, страница отсутствует: {row}",
            ))

    return {
        "pgexercises_manifest_exists": True,
        "error_rows_count": len(error_rows),
        "missing_pages_count": len(missing_pages),
        "existing_error_pages_count": len(existing_error_pages),
        "error_rows": error_rows,
    }


def check_service_junk(corpus_root: Path, findings: list[Finding]) -> dict[str, Any]:
    pycache_dirs = [p for p in corpus_root.rglob("__pycache__") if p.is_dir()]
    pyc_files = [p for p in corpus_root.rglob("*.pyc") if p.is_file()]
    bak_files = [p for p in corpus_root.rglob("*.bak") if p.is_file()]
    bak_manifest_files = [p for p in corpus_root.rglob("download_manifest.jsonl.bak*") if p.is_file()]

    backup_dirs = []
    for p in corpus_root.rglob("*"):
        if p.is_dir() and ("backup" in p.name.lower() or p.name.startswith("_backup")):
            backup_dirs.append(p)

    for p in pycache_dirs:
        findings.append(Finding(
            "ERROR",
            "PYCACHE_DIR_REMAINS",
            rel(p, corpus_root),
            "__pycache__ не должен оставаться в финальном корпусе",
        ))

    for p in pyc_files:
        findings.append(Finding(
            "ERROR",
            "PYC_FILE_REMAINS",
            rel(p, corpus_root),
            ".pyc файл не должен оставаться в финальном корпусе",
        ))

    for p in bak_manifest_files:
        findings.append(Finding(
            "ERROR",
            "BACKUP_MANIFEST_REMAINS",
            rel(p, corpus_root),
            "download_manifest.jsonl.bak* не должен оставаться в финальном корпусе",
        ))

    # Обычные .bak тоже лучше подсветить, но backup before fix можно оставить как warning.
    for p in bak_files:
        findings.append(Finding(
            "WARNING",
            "BAK_FILE_REMAINS",
            rel(p, corpus_root),
            "Найден .bak файл. Проверь, нужен ли он перед финальным embeddings.",
        ))

    return {
        "pycache_dirs_count": len(pycache_dirs),
        "pycache_dirs": [rel(p, corpus_root) for p in pycache_dirs],
        "pyc_files_count": len(pyc_files),
        "pyc_files": [rel(p, corpus_root) for p in pyc_files],
        "bak_files_count": len(bak_files),
        "bak_files": [rel(p, corpus_root) for p in bak_files],
        "backup_dirs_count": len(backup_dirs),
        "backup_dirs": [rel(p, corpus_root) for p in backup_dirs],
    }


def check_ingestion_policy(corpus_root: Path, findings: list[Finding]) -> dict[str, Any]:
    policy_path = corpus_root / "tutorial" / "external_registry" / "ingestion_policy.json"

    required_index_fragments = [
        "corpus/postgres/html/**/*.html",
        "corpus/tutorial/curated/**/*.md",
        "corpus/tutorial/processed_html/**/*.md",
    ]

    required_do_not_index_fragments = [
        "corpus/tutorial/html/**/*.html",
        "corpus/tutorial/external_registry/**",
        "corpus/tutorial/scripts/**",
        "corpus/tutorial/*REPORT*",
        "corpus/tutorial/*MANIFEST*",
        "corpus/tutorial/**/__pycache__/**",
        "corpus/tutorial/**/*.pyc",
        "corpus/tutorial/**/_backup*/**",
        "download_manifest.jsonl.bak*",
    ]

    if not policy_path.exists():
        findings.append(Finding(
            "ERROR",
            "INGESTION_POLICY_MISSING",
            rel(policy_path, corpus_root),
            "Не найден ingestion_policy.json",
        ))
        return {"exists": False}

    text = read_text(policy_path)
    missing_index = [x for x in required_index_fragments if x not in text]
    missing_deny = [x for x in required_do_not_index_fragments if x not in text]

    for x in missing_index:
        findings.append(Finding(
            "ERROR",
            "INGESTION_POLICY_INDEX_RULE_MISSING",
            rel(policy_path, corpus_root),
            f"В ingestion policy отсутствует обязательное INDEX правило: {x}",
        ))

    for x in missing_deny:
        findings.append(Finding(
            "ERROR",
            "INGESTION_POLICY_DENY_RULE_MISSING",
            rel(policy_path, corpus_root),
            f"В ingestion policy отсутствует обязательное DO_NOT_INDEX правило: {x}",
        ))

    return {
        "exists": True,
        "missing_index_rules": missing_index,
        "missing_do_not_index_rules": missing_deny,
    }


def update_quality_report(corpus_root: Path, audit: dict[str, Any]) -> None:
    qpath = corpus_root / "tutorial" / "QUALITY_REPORT.json"
    existing: dict[str, Any] = {}

    if qpath.exists():
        try:
            existing = json.loads(read_text(qpath))
        except Exception:
            existing = {}

    existing["strict_audit_updated_at"] = now_iso()
    existing["strict_validator"] = {
        "ready_for_chunking_and_embeddings": audit["ready_for_chunking_and_embeddings"],
        "errors_count": audit["errors_count"],
        "warnings_count": audit["warnings_count"],
        "summary": audit["summary"],
        "top_errors": audit["errors"][:50],
        "top_warnings": audit["warnings"][:50],
    }

    # Эти поля специально перезаписываем, чтобы старый errors_count=0 больше не вводил в заблуждение.
    existing["errors_count"] = audit["errors_count"]
    existing["warnings_count"] = audit["warnings_count"]
    existing["CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS"] = audit["ready_for_chunking_and_embeddings"]

    dump_json(qpath, existing)


def write_final_markdown_report(corpus_root: Path, audit: dict[str, Any]) -> None:
    report_path = corpus_root / "CORPUS_FINAL_AUDIT_REPORT.md"
    lines = []

    lines.append("# Corpus Final Audit Report")
    lines.append("")
    lines.append(f"Generated at: `{audit['generated_at']}`")
    lines.append("")
    lines.append(f"`CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS = {str(audit['ready_for_chunking_and_embeddings']).lower()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in audit["summary"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.append("")
    lines.append("## Errors")
    lines.append("")
    if audit["errors"]:
        for item in audit["errors"]:
            lines.append(f"- **{item['code']}** — `{item['path']}` — {item['message']}")
    else:
        lines.append("No errors.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if audit["warnings"]:
        for item in audit["warnings"]:
            lines.append(f"- **{item['code']}** — `{item['path']}` — {item['message']}")
    else:
        lines.append("No warnings.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_self_as_validator(corpus_root: Path) -> None:
    target = corpus_root / "tutorial" / "scripts" / "validate_corpus_before_embeddings.py"
    target.parent.mkdir(parents=True, exist_ok=True)

    source = Path(__file__).resolve()
    if source == target.resolve():
        return

    shutil.copy2(source, target)
    target.chmod(0o755)


def run_audit(corpus_root: Path) -> dict[str, Any]:
    corpus_root = corpus_root.resolve()
    findings: list[Finding] = []

    official_counts = check_official(corpus_root, findings)
    curated = check_curated(corpus_root, findings)
    processed = check_processed_html(corpus_root, findings)
    pgex = check_pgexercises_manifest(corpus_root, findings)
    service = check_service_junk(corpus_root, findings)
    ingestion = check_ingestion_policy(corpus_root, findings)

    curated_md_count = count_files(corpus_root / "tutorial" / "curated", "*.md")
    processed_md_count = count_files(corpus_root / "tutorial" / "processed_html", "*.md")
    raw_html_count = count_files(corpus_root / "tutorial" / "html", "*.html")

    errors = [asdict(f) for f in findings if f.level == "ERROR"]
    warnings = [asdict(f) for f in findings if f.level == "WARNING"]

    ready = len(errors) == 0

    audit = {
        "generated_at": now_iso(),
        "corpus_root": str(corpus_root),
        "ready_for_chunking_and_embeddings": ready,
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "summary": {
            "official_html_16": official_counts.get("16", 0),
            "official_html_17": official_counts.get("17", 0),
            "official_html_18": official_counts.get("18", 0),
            "curated_md_files": curated_md_count,
            "processed_html_md_files": processed_md_count,
            "raw_tutorial_html_files_not_for_indexing": raw_html_count,
            "broken_official_backing_count": curated["broken_official_backing_count"],
            "forbidden_curated_hits_count": curated["forbidden_curated_hits_count"],
            "processed_missing_source_url_count": processed["missing_source_url_count"],
            "processed_source_url_mismatch_count": processed["source_url_mismatch_count"],
            "pgexercises_boilerplate_count": processed["pgexercises_boilerplate_count"],
            "pgexercises_manifest_error_rows_count": pgex["error_rows_count"],
            "pycache_dirs_count": service["pycache_dirs_count"],
            "pyc_files_count": service["pyc_files_count"],
            "bak_files_count": service["bak_files_count"],
            "ingestion_policy_exists": ingestion.get("exists", False),
        },
        "details": {
            "official": official_counts,
            "curated": curated,
            "processed_html": processed,
            "pgexercises_manifest": pgex,
            "service_junk": service,
            "ingestion_policy": ingestion,
        },
        "errors": errors,
        "warnings": warnings,
    }

    return audit


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Strict corpus audit before chunking and embeddings."
    )
    parser.add_argument(
        "--corpus-root",
        required=True,
        type=Path,
        help="Путь до папки corpus, например /home/arz/Desktop/RAG_postgres/corpus",
    )
    parser.add_argument(
        "--no-update-quality-report",
        action="store_true",
        help="Не обновлять corpus/tutorial/QUALITY_REPORT.json",
    )
    parser.add_argument(
        "--no-install-validator",
        action="store_true",
        help="Не копировать этот скрипт в corpus/tutorial/scripts/validate_corpus_before_embeddings.py",
    )

    args = parser.parse_args()
    corpus_root = args.corpus_root.resolve()

    if not corpus_root.exists():
        raise SystemExit(f"corpus-root не найден: {corpus_root}")

    audit = run_audit(corpus_root)

    audit_json_path = corpus_root / "CORPUS_FINAL_AUDIT_REPORT.json"
    dump_json(audit_json_path, audit)
    write_final_markdown_report(corpus_root, audit)

    if not args.no_update_quality_report:
        update_quality_report(corpus_root, audit)

    if not args.no_install_validator:
        install_self_as_validator(corpus_root)

    print(json.dumps({
        "corpus_root": str(corpus_root),
        "errors_count": audit["errors_count"],
        "warnings_count": audit["warnings_count"],
        "summary": audit["summary"],
        "CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS": audit["ready_for_chunking_and_embeddings"],
        "audit_json": str(audit_json_path),
        "audit_markdown": str(corpus_root / "CORPUS_FINAL_AUDIT_REPORT.md"),
        "quality_report_updated": not args.no_update_quality_report,
        "validator_installed_to": str(corpus_root / "tutorial" / "scripts" / "validate_corpus_before_embeddings.py"),
    }, ensure_ascii=False, indent=2))

    if audit["ready_for_chunking_and_embeddings"]:
        print("CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS = true")
        raise SystemExit(0)

    print("CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS = false")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
