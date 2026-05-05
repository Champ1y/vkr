#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import sys

WIKI_JUNK_PATTERNS = ["Special:", "Category:", "Talk:", "User:", "PostgreSQL_wiki:"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(rel: str) -> tuple[str, bool]:
    if rel.startswith("curated/") and rel.endswith(".md"):
        return "curated_markdown", True
    if rel.startswith("processed_html/") and rel.endswith(".md"):
        return "processed_html_markdown", True
    if rel.startswith("html/") and rel.endswith(".html"):
        return "raw_html_archive", False
    if rel.startswith("external_registry/") and rel.endswith(".json"):
        return "external_registry", False
    if rel.startswith("scripts/") and rel.endswith(".py"):
        return "script", False
    if rel in {"QUALITY_REPORT.json", "README_IDEAL.md"}:
        return "report", False
    if rel.endswith("MANIFEST_IDEAL.json"):
        return "report", False
    return "report", False


def has_yaml_front_matter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text


def main() -> int:
    tutorial_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("corpus/tutorial")
    tutorial_root = tutorial_root.resolve()
    corpus_root = tutorial_root.parent
    official_root = corpus_root / "postgres/html"

    if not tutorial_root.exists():
        raise SystemExit(f"Root not found: {tutorial_root}")

    all_files = sorted([p for p in tutorial_root.rglob("*") if p.is_file()])
    curated_files = sorted((tutorial_root / "curated").glob("*/*.md")) if (tutorial_root / "curated").exists() else []
    raw_html_files = sorted((tutorial_root / "html").rglob("*.html")) if (tutorial_root / "html").exists() else []
    processed_md_files = sorted((tutorial_root / "processed_html").rglob("*.md")) if (tutorial_root / "processed_html").exists() else []

    pg_raw = list((tutorial_root / "html" / "pgexercises").rglob("*.html")) if (tutorial_root / "html" / "pgexercises").exists() else []
    wiki_raw = list((tutorial_root / "html" / "postgres_wiki_whitelist").rglob("*.html")) if (tutorial_root / "html" / "postgres_wiki_whitelist").exists() else []

    official_counts = {}
    for v in ("16", "17", "18"):
        d = official_root / v
        official_counts[v] = len(list(d.glob("*.html"))) if d.exists() else 0

    # Exclude MANIFEST_IDEAL.json from hash listing to avoid self-hash mismatch.
    manifest_files: list[dict] = []
    for p in all_files:
        rel = p.relative_to(tutorial_root).as_posix()
        if rel == "MANIFEST_IDEAL.json":
            continue
        role, indexable = classify(rel)
        manifest_files.append(
            {
                "path": rel,
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
                "role": role,
                "indexable": indexable,
            }
        )

    counts = {
        "total_files": len(all_files),
        "curated_md_files": len(curated_files),
        "raw_html_files": len(raw_html_files),
        "processed_html_md_files": len(processed_md_files),
        "pgexercises_raw_html_files": len(pg_raw),
        "wiki_raw_html_files": len(wiki_raw),
        "external_registry_files": len(list((tutorial_root / "external_registry").glob("*.json"))) if (tutorial_root / "external_registry").exists() else 0,
        "scripts_count": len(list((tutorial_root / "scripts").glob("*.py"))) if (tutorial_root / "scripts").exists() else 0,
        "json_files": len([p for p in all_files if p.suffix.lower() == ".json"]),
        "sql_files": len([p for p in all_files if p.suffix.lower() == ".sql"]),
        "official_html_files_16": official_counts["16"],
        "official_html_files_17": official_counts["17"],
        "official_html_files_18": official_counts["18"],
        "indexable_files_count": sum(1 for x in manifest_files if x["indexable"]),
        "non_indexable_archive_files_count": sum(1 for x in manifest_files if x["role"] == "raw_html_archive" and not x["indexable"]),
    }

    errors: list[str] = []

    placeholder_hits = []
    docs_placeholder_hits = []
    for p in curated_files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if "{v}" in t:
            placeholder_hits.append(p.relative_to(tutorial_root).as_posix())
        if "docs/{v}" in t:
            docs_placeholder_hits.append(p.relative_to(tutorial_root).as_posix())

    if placeholder_hits:
        errors.append(f"Placeholders remain: {len(placeholder_hits)}")
    if docs_placeholder_hits:
        errors.append(f"docs/{{v}} placeholders remain: {len(docs_placeholder_hits)}")

    wiki_junk_paths = [
        p.relative_to(tutorial_root).as_posix()
        for p in raw_html_files
        if any(tok in p.as_posix() for tok in WIKI_JUNK_PATTERNS)
    ]
    if wiki_junk_paths:
        errors.append(f"Wiki junk paths remain: {len(wiki_junk_paths)}")

    curated_missing_yaml = []
    curated_missing_backing = []
    for p in curated_files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if not has_yaml_front_matter(t):
            curated_missing_yaml.append(p.relative_to(tutorial_root).as_posix())
            continue
        meta = t.split("\n---\n", 1)[0][4:]
        if not re.search(r"(?m)^official_backing\s*:", meta):
            curated_missing_backing.append(p.relative_to(tutorial_root).as_posix())

    if curated_missing_yaml:
        errors.append(f"Curated without YAML: {len(curated_missing_yaml)}")
    if curated_missing_backing:
        errors.append(f"Curated without official_backing: {len(curated_missing_backing)}")

    processed_missing_yaml = []
    for p in processed_md_files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if not has_yaml_front_matter(t):
            processed_missing_yaml.append(p.relative_to(tutorial_root).as_posix())
    if processed_missing_yaml:
        errors.append(f"Processed markdown without YAML: {len(processed_missing_yaml)}")

    raw_html_indexable_bad = [x["path"] for x in manifest_files if x["role"] == "raw_html_archive" and x["indexable"]]
    processed_not_indexable_bad = [x["path"] for x in manifest_files if x["role"] == "processed_html_markdown" and not x["indexable"]]
    if raw_html_indexable_bad:
        errors.append(f"Raw HTML incorrectly indexable: {len(raw_html_indexable_bad)}")
    if processed_not_indexable_bad:
        errors.append(f"Processed markdown not indexable: {len(processed_not_indexable_bad)}")

    generated_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")

    quality_report = {
        "generated_at": generated_at,
        "corpus_root": tutorial_root.as_posix(),
        "counts": counts,
        "validation": {
            "placeholders_empty": len(placeholder_hits) == 0,
            "docs_placeholder_empty": len(docs_placeholder_hits) == 0,
            "wiki_junk_paths_empty": len(wiki_junk_paths) == 0,
            "all_curated_have_yaml": len(curated_missing_yaml) == 0,
            "all_curated_have_official_backing": len(curated_missing_backing) == 0,
            "all_processed_have_yaml": len(processed_missing_yaml) == 0,
            "raw_html_indexable_false": len(raw_html_indexable_bad) == 0,
            "processed_html_indexable_true": len(processed_not_indexable_bad) == 0,
            "manifest_self_hash_excluded": True,
        },
        "errors_count": len(errors),
        "errors": errors,
        "details": {
            "placeholder_hits": placeholder_hits,
            "docs_placeholder_hits": docs_placeholder_hits,
            "wiki_junk_paths": wiki_junk_paths,
            "curated_missing_yaml": curated_missing_yaml,
            "curated_missing_official_backing": curated_missing_backing,
            "processed_missing_yaml": processed_missing_yaml,
            "raw_html_indexable_bad": raw_html_indexable_bad,
            "processed_not_indexable_bad": processed_not_indexable_bad,
        },
        "indexing_policy_summary": {
            "raw_html_indexable": False,
            "processed_html_indexable": True,
            "curated_markdown_indexable": True,
            "official_required_for_factual_answers": True,
        },
    }

    manifest = {
        "generated_at": generated_at,
        "name": "ideal_postgresql_tutorial_supplementary_corpus",
        "root": tutorial_root.as_posix(),
        "counts": counts,
        "self_hash_excluded": True,
        "files": sorted(manifest_files, key=lambda x: x["path"]),
    }

    (tutorial_root / "QUALITY_REPORT.json").write_text(
        json.dumps(quality_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (tutorial_root / "MANIFEST_IDEAL.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "quality_report": str(tutorial_root / "QUALITY_REPORT.json"),
                "manifest": str(tutorial_root / "MANIFEST_IDEAL.json"),
                "counts": counts,
                "errors_count": len(errors),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
