import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = PROJECT_ROOT / "corpus"

manifest_files = list(CORPUS_ROOT.rglob("download_manifest.jsonl"))

if not manifest_files:
    raise SystemExit("download_manifest.jsonl не найден")

changed_total = 0

for manifest_path in manifest_files:
    fixed_lines = []
    changed = 0

    # Определяем версию по пути файла
    # Например: corpus/postgres/html/18/download_manifest.jsonl
    parts = manifest_path.parts
    pg_version = None
    for part in parts:
        if part in {"16", "17", "18"}:
            pg_version = part
            break

    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)

            source_url = item.get("source_url")
            version = str(item.get("version") or item.get("pg_major_version") or pg_version)

            if source_url and version in {"16", "17", "18"}:
                old_url = source_url
                source_url = source_url.replace(
                    "https://www.postgresql.org/docs/current/",
                    f"https://www.postgresql.org/docs/{version}/",
                )
                source_url = source_url.replace(
                    "/docs/current/",
                    f"/docs/{version}/",
                )

                if source_url != old_url:
                    item["source_url"] = source_url
                    changed += 1

            fixed_lines.append(json.dumps(item, ensure_ascii=False))

    if changed:
        backup_path = manifest_path.with_suffix(manifest_path.suffix + ".bak")
        manifest_path.rename(backup_path)

        with manifest_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(fixed_lines) + "\n")

        print(f"OK: {manifest_path} | fixed {changed} urls | backup: {backup_path}")
        changed_total += changed
    else:
        print(f"SKIP: {manifest_path} | no current urls")

print(f"Done. Total fixed urls: {changed_total}")
