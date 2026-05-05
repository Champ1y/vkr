#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import json, re, sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tutorial")
if not root.exists():
    raise SystemExit(f"Root not found: {root}")

md_files = list((root / "curated").glob("*/*.md"))
html_files = list((root / "html").rglob("*.html"))

errors = []
for md in md_files:
    text = md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        errors.append(f"No YAML front matter: {md}")
        continue
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"Broken YAML front matter: {md}")
        continue
    meta = parts[1]
    for required in ["pg_version:", "language:", "corpus_type:", "source_role:", "official_backing:"]:
        if required not in meta:
            errors.append(f"Missing {required} in {md}")

wiki_junk_patterns = ["Special:", "Category:", "Talk:", "User:", "PostgreSQL_wiki:"]
for html in html_files:
    s = str(html)
    if any(p in s for p in wiki_junk_patterns):
        errors.append(f"Wiki junk remains: {html}")

summary = {
    "root": str(root),
    "curated_md_files": len(md_files),
    "html_files": len(html_files),
    "pgexercises_files": len(list((root / "html" / "pgexercises").rglob("*"))) if (root / "html" / "pgexercises").exists() else 0,
    "wiki_whitelist_html_files": len(list((root / "html" / "postgres_wiki_whitelist").rglob("*.html"))) if (root / "html" / "postgres_wiki_whitelist").exists() else 0,
    "errors_count": len(errors),
    "errors": errors[:100],
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
