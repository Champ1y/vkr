#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

CURATED_ROOT = Path("corpus/tutorial/curated")
TUTORIAL_ROOT = Path("corpus/tutorial")
BACKUP_ROOT = Path("corpus/tutorial/_backup_before_official_backing_fix")
OFFICIAL_ROOT = Path("corpus/postgres/html")

URL_RE = re.compile(r"^https://www\.postgresql\.org/docs/(16|17|18)/([^/]+\.html)$")
URL_ANY_RE = re.compile(r"https://www\.postgresql\.org/docs/(16|17|18)/([^/]+\.html)")


@dataclass
class FileChange:
    path: Path
    changed_front_matter: bool
    changed_body: bool


def replacement_urls(version: str, page: str) -> List[str] | None:
    base = f"https://www.postgresql.org/docs/{version}/"

    if page == "view-pg-stat-activity.html":
        return [
            base + "monitoring-stats.html",
            base + "monitoring.html",
        ]

    if page in {"view-pg-stat-replication.html", "view-pg-stat-subscription.html"}:
        return [
            base + "monitoring-stats.html",
            base + "logical-replication-monitoring.html",
            base + "view-pg-replication-slots.html",
        ]

    if page == "view-pg-extension.html":
        return [
            base + "catalog-pg-extension.html",
            base + "view-pg-available-extensions.html",
            base + "view-pg-available-extension-versions.html",
        ]

    if page == "streaming-replication.html":
        return [
            base + "warm-standby.html",
            base + "different-replication-solutions.html",
            base + "runtime-config-replication.html",
        ]

    if page == "runtime-config-autovacuum.html" and version == "18":
        return [base + "runtime-config-vacuum.html"]

    return None


def split_front_matter(text: str) -> Tuple[str, str, str] | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    prefix = "---"
    meta = parts[1]
    body = parts[2]
    return prefix, meta, body


def parse_official_backing_block(meta: str) -> Tuple[List[str], int, int, str] | None:
    lines = meta.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "official_backing:":
            start = i
            break
    if start is None:
        return None

    items: List[str] = []
    i = start + 1
    indent = "  "
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(\s*)-\s+\"([^\"]+)\"\s*$", ln)
        if not m:
            break
        if i == start + 1:
            indent = m.group(1)
        items.append(m.group(2))
        i += 1
    end = i
    return items, start, end, indent


def rebuild_meta_with_official_backing(meta: str, new_items: List[str], start: int, end: int, indent: str) -> str:
    lines = meta.splitlines()
    new_lines = [f'{indent}- "{u}"' for u in new_items]
    lines[start + 1:end] = new_lines
    return "\n".join(lines) + ("\n" if meta.endswith("\n") else "")


def dedupe_preserve(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def transform_official_backing(items: List[str], replacement_counter: Dict[str, int]) -> List[str]:
    out: List[str] = []
    seen = set()
    for u in items:
        m = URL_RE.match(u)
        reps = None
        if m:
            version, page = m.group(1), m.group(2)
            reps = replacement_urls(version, page)
        if reps is None:
            candidates = [u]
        else:
            candidates = reps
            replacement_counter[f"{page}"] = replacement_counter.get(page, 0) + 1

        for c in candidates:
            if c not in seen:
                seen.add(c)
                out.append(c)
    return out


def replace_body_known_urls(body: str, replacement_counter: Dict[str, int]) -> str:
    lines = body.splitlines()
    changed = False

    for idx, line in enumerate(lines):
        matched = False
        for m in URL_ANY_RE.finditer(line):
            version, page = m.group(1), m.group(2)
            old_url = m.group(0)
            reps = replacement_urls(version, page)
            if reps is None:
                continue

            bullet = re.match(r"^(\s*-\s*)(`?)" + re.escape(old_url) + r"(`?)\s*$", line)
            if bullet:
                prefix, t1, t2 = bullet.group(1), bullet.group(2), bullet.group(3)
                tick = "`" if (t1 == "`" or t2 == "`") else ""
                repl_lines = [f"{prefix}{tick}{u}{tick}" for u in dedupe_preserve(reps)]
                lines[idx] = "\n".join(repl_lines)
                replacement_counter[f"body::{page}"] = replacement_counter.get(f"body::{page}", 0) + 1
                changed = True
                matched = True
            else:
                # conservative fallback: replace inline URL with first replacement only
                line2 = line.replace(old_url, reps[0])
                if line2 != line:
                    lines[idx] = line2
                    replacement_counter[f"body_inline::{page}"] = replacement_counter.get(f"body_inline::{page}", 0) + 1
                    changed = True
                    matched = True
            if matched:
                break

    if not changed:
        return body
    joined = "\n".join(lines)
    if body.endswith("\n"):
        joined += "\n"
    return joined


def collect_official_backing_urls(curated_files: List[Path]) -> List[Tuple[Path, str]]:
    found: List[Tuple[Path, str]] = []
    for p in curated_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_front_matter(text)
        if not parts:
            continue
        _, meta, _ = parts
        block = parse_official_backing_block(meta)
        if not block:
            continue
        items, *_ = block
        for u in items:
            found.append((p, u))
    return found


def check_broken_urls(curated_files: List[Path]) -> List[Tuple[Path, str, Path]]:
    broken: List[Tuple[Path, str, Path]] = []
    for p, u in collect_official_backing_urls(curated_files):
        m = URL_RE.match(u)
        if not m:
            continue
        v, page = m.group(1), m.group(2)
        local = OFFICIAL_ROOT / v / page
        if not local.exists():
            broken.append((p, u, local))
    return broken


def backup_file(path: Path) -> None:
    rel = path.relative_to(TUTORIAL_ROOT)
    dst = BACKUP_ROOT / rel
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)


def run_fix(check_only: bool) -> dict:
    curated_files = sorted(CURATED_ROOT.glob("16/*.md")) + sorted(CURATED_ROOT.glob("17/*.md")) + sorted(CURATED_ROOT.glob("18/*.md"))

    replacement_counter: Dict[str, int] = {}
    file_changes: List[FileChange] = []
    changed_paths: List[Path] = []

    for p in curated_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_front_matter(text)
        if not parts:
            continue
        _, meta, body = parts

        block = parse_official_backing_block(meta)
        if not block:
            continue
        items, start, end, indent = block

        new_items = transform_official_backing(items, replacement_counter)
        new_meta = rebuild_meta_with_official_backing(meta, new_items, start, end, indent)

        new_body = replace_body_known_urls(body, replacement_counter)

        changed_meta = (new_meta != meta)
        changed_body = (new_body != body)
        if changed_meta or changed_body:
            file_changes.append(FileChange(path=p, changed_front_matter=changed_meta, changed_body=changed_body))
            changed_paths.append(p)
            if not check_only:
                backup_file(p)
                new_text = "---" + new_meta + "---" + new_body
                p.write_text(new_text, encoding="utf-8")

    broken = check_broken_urls(curated_files)

    result = {
        "checked_files": len(curated_files),
        "changed_files": len(changed_paths),
        "changed_paths": [str(x) for x in changed_paths],
        "replacement_counter": replacement_counter,
        "broken_official_backing_count": len(broken),
        "broken_official_backing": [
            {
                "file": str(p),
                "url": u,
                "expected_local_file": str(local),
            }
            for p, u, local in broken
        ],
        "check_only": check_only,
    }
    return result


def write_report(result: dict) -> None:
    report_path = Path("corpus/tutorial/OFFICIAL_BACKING_FIX_REPORT.md")
    lines = []
    lines.append("# Official Backing Fix Report")
    lines.append("")
    lines.append(f"- Curated files checked: **{result['checked_files']}**")
    lines.append(f"- Files changed: **{result['changed_files']}**")
    lines.append("")
    lines.append("## Changed files")
    if result["changed_paths"]:
        for p in result["changed_paths"]:
            lines.append(f"- `{p}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Replacement counters")
    if result["replacement_counter"]:
        for k in sorted(result["replacement_counter"]):
            lines.append(f"- `{k}`: {result['replacement_counter'][k]}")
    else:
        lines.append("- No replacements applied")
    lines.append("")
    lines.append("## Remaining broken official_backing links")
    if result["broken_official_backing"]:
        for b in result["broken_official_backing"]:
            lines.append(f"- `{b['file']}` -> `{b['url']}` (missing `{b['expected_local_file']}`)")
    else:
        lines.append("- None")
    lines.append("")
    lines.append(f"- broken official_backing count = **{result['broken_official_backing_count']}**")
    lines.append("- official corpus was not modified by this script")
    lines.append("- chunks and embeddings were not recalculated")
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fix curated official_backing links and validate local official files.")
    ap.add_argument("--check-only", action="store_true", help="Do not write changes; only validate and report.")
    args = ap.parse_args()

    if not CURATED_ROOT.exists():
        raise SystemExit(f"Curated root not found: {CURATED_ROOT}")
    if not OFFICIAL_ROOT.exists():
        raise SystemExit(f"Official root not found: {OFFICIAL_ROOT}")

    result = run_fix(check_only=args.check_only)

    if not args.check_only:
        write_report(result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["broken_official_backing_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
