#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import difflib
import json
import re
import sys


def split_yaml_body(text: str) -> tuple[str, str]:
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return '', text


def normalize_for_compare(body: str) -> str:
    s = body
    s = re.sub(r'/docs/(16|17|18)/', '/docs/XX/', s)
    s = re.sub(r'PostgreSQL\s+(16|17|18)', 'PostgreSQL XX', s)
    s = re.sub(r'pg_version\s*=\s*["\']?(16|17|18)["\']?', 'pg_version=XX', s)
    return s


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('tutorial')
    curated_root = root / 'curated'
    versions = ['16', '17', '18']

    if not curated_root.exists():
        raise SystemExit(f'curated root not found: {curated_root}')

    by_topic: dict[str, dict[str, Path]] = {}
    for ver in versions:
        for p in sorted((curated_root / ver).glob('*.md')):
            by_topic.setdefault(p.name, {})[ver] = p

    special_version_topics = {'major_upgrade_notes.ru.md', 'version_and_release_notes.ru.md'}

    rows = []
    for topic, mp in sorted(by_topic.items()):
        if set(mp.keys()) != set(versions):
            continue

        texts = {v: mp[v].read_text(encoding='utf-8', errors='replace') for v in versions}
        bodies = {v: split_yaml_body(texts[v])[1] for v in versions}
        norms = {v: normalize_for_compare(bodies[v]) for v in versions}

        identical_norm = (norms['16'] == norms['17'] == norms['18'])
        materially_different = not identical_norm
        has_version_specific_section = any('## Версионная привязка' in bodies[v] for v in versions)

        needs_version_note = (
            identical_norm
            and not has_version_specific_section
            and topic not in special_version_topics
        )

        rows.append({
            'topic_file': topic,
            'identical_except_version_urls': identical_norm,
            'materially_different': materially_different,
            'has_version_specific_section': has_version_specific_section,
            'needs_version_note': needs_version_note,
            'sim_ratio_16_17': round(difflib.SequenceMatcher(None, bodies['16'], bodies['17']).ratio(), 5),
            'sim_ratio_16_18': round(difflib.SequenceMatcher(None, bodies['16'], bodies['18']).ratio(), 5),
        })

    out = {
        'total_topics': len(rows),
        'identical_except_version_urls_count': sum(1 for r in rows if r['identical_except_version_urls']),
        'materially_different_count': sum(1 for r in rows if r['materially_different']),
        'needs_version_note_count': sum(1 for r in rows if r['needs_version_note']),
        'topics': rows,
    }

    output_path = root / 'external_registry' / 'curated_version_comparison.json'
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'report_path': str(output_path),
        'total_topics': out['total_topics'],
        'identical_except_version_urls_count': out['identical_except_version_urls_count'],
        'materially_different_count': out['materially_different_count'],
        'needs_version_note_count': out['needs_version_note_count'],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
