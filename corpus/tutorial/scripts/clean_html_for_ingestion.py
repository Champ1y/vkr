#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

from bs4 import BeautifulSoup

REMOVE_TAGS = {
    "script", "style", "noscript", "nav", "footer", "header", "aside", "form", "button", "svg"
}
REMOVE_ATTR_PATTERNS = [
    "navigation", "navbox", "footer", "sidebar", "toc", "search",
    "mw-navigation", "mw-footer", "printfooter", "catlinks", "vector-menu", "sitesub"
]
USAGE_RULE = (
    "Использовать только как supplementary слой в tutorial + extended_mode. "
    "Факты должны подтверждаться official corpus выбранной версии."
)


def collapse_blank_lines(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines()]
    out = []
    prev_blank = False
    for ln in lines:
        blank = (ln == "")
        if blank:
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(ln)
            prev_blank = False
    return "\n".join(out).strip()


def escape_yaml(value: str) -> str:
    return value.replace('"', '\"')


def infer_source_role(rel_html_path: Path) -> str:
    first = rel_html_path.parts[0] if rel_html_path.parts else ""
    if first == "pgexercises":
        return "external_exercise"
    if first == "postgres_wiki_whitelist":
        return "external_troubleshooting_whitelist"
    return "external_troubleshooting_whitelist"


def clean_one(html_path: Path, html_root: Path, out_root: Path) -> Path:
    rel = html_path.relative_to(html_root)
    out_path = (out_root / rel).with_suffix('.md')
    out_path.parent.mkdir(parents=True, exist_ok=True)

    raw = html_path.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(raw, 'html.parser')

    title = ""
    if soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(strip=True)
    else:
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)
    if not title:
        title = html_path.stem

    for tag in list(soup.find_all(REMOVE_TAGS)):
        tag.decompose()

    for node in list(soup.find_all(True)):
        if getattr(node, 'attrs', None) is None:
            continue
        attrs = []
        node_id = node.get('id')
        if node_id:
            attrs.append(str(node_id))
        classes = node.get('class')
        if classes:
            if isinstance(classes, (list, tuple)):
                attrs.extend(str(c) for c in classes)
            else:
                attrs.append(str(classes))
        low_attrs = " ".join(attrs).lower()
        if low_attrs and any(p in low_attrs for p in REMOVE_ATTR_PATTERNS):
            node.decompose()

    text = soup.get_text(separator='\n', strip=True)
    text = collapse_blank_lines(text)

    rel_original = (Path('html') / rel).as_posix()
    source_role = infer_source_role(rel)

    md = (
        "---\n"
        f"title: \"{escape_yaml(title)}\"\n"
        "language: \"en\"\n"
        "corpus_type: \"supplementary\"\n"
        f"source_role: \"{source_role}\"\n"
        "source_format: \"html_cleaned_to_markdown\"\n"
        f"original_html_path: \"{escape_yaml(rel_original)}\"\n"
        "indexable: true\n"
        f"usage_rule: \"{escape_yaml(USAGE_RULE)}\"\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{text}\n"
    )

    out_path.write_text(md, encoding='utf-8')
    return out_path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('tutorial')
    html_root = root / 'html'
    out_root = root / 'processed_html'

    if not html_root.exists():
        raise SystemExit(f"HTML root not found: {html_root}")

    html_files = sorted(html_root.rglob('*.html'))
    generated = []
    for hp in html_files:
        generated.append(clean_one(hp, html_root, out_root))

    summary = {
        'root': str(root),
        'html_files': len(html_files),
        'processed_markdown_files': len(generated),
        'output_root': str(out_root),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
