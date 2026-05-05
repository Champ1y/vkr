#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

BANNED_HTML_MARKERS = ["<script", "<style", "<nav", "<footer"]


def has_yaml_front_matter(text: str) -> bool:
    if not text.startswith('---'):
        return False
    parts = text.split('---', 2)
    return len(parts) >= 3


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('tutorial')
    source_root = root / 'html'
    processed_root = root / 'processed_html'

    errors = []
    html_files = sorted(source_root.rglob('*.html')) if source_root.exists() else []

    if not processed_root.exists():
        errors.append(f"processed_html not found: {processed_root}")
        processed_files = []
    else:
        processed_files = sorted(processed_root.rglob('*.md'))

    if len(processed_files) != len(html_files):
        errors.append(
            f"processed/html count mismatch: processed={len(processed_files)} html={len(html_files)}"
        )

    for p in processed_files:
        text = p.read_text(encoding='utf-8', errors='replace')
        if not has_yaml_front_matter(text):
            errors.append(f"No YAML front matter: {p}")
            continue
        parts = text.split('---', 2)
        body = parts[2].strip() if len(parts) >= 3 else ''
        if not body:
            errors.append(f"Empty processed content: {p}")
        low = text.lower()
        for marker in BANNED_HTML_MARKERS:
            if marker in low:
                errors.append(f"Banned HTML marker '{marker}' found in {p}")
                break

    summary = {
        'root': str(root),
        'source_html_files': len(html_files),
        'processed_markdown_files': len(processed_files),
        'errors_count': len(errors),
        'errors': errors[:200],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
