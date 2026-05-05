import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = PROJECT_ROOT / "corpus"

manifest_files = list(CORPUS_ROOT.rglob("download_manifest.jsonl"))

if not manifest_files:
    raise SystemExit("download_manifest.jsonl не найден")

for manifest_path in manifest_files:
    fixed_lines = []

    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)

            local_path = item.get("local_path")
            if local_path:
                path = Path(local_path)

                if path.is_absolute():
                    try:
                        rel_path = path.resolve().relative_to(PROJECT_ROOT)
                    except ValueError:
                        # Если путь абсолютный, но не внутри текущего проекта,
                        # пробуем восстановить путь начиная с папки corpus.
                        parts = path.parts
                        if "corpus" in parts:
                            idx = parts.index("corpus")
                            rel_path = Path(*parts[idx:])
                        else:
                            raise ValueError(f"Не могу сделать относительный путь: {path}")

                    item["local_path"] = rel_path.as_posix()

            fixed_lines.append(json.dumps(item, ensure_ascii=False))

    backup_path = manifest_path.with_suffix(manifest_path.suffix + ".bak")
    manifest_path.rename(backup_path)

    with manifest_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(fixed_lines) + "\n")

    print(f"OK: {manifest_path}")
    print(f"Backup: {backup_path}")
