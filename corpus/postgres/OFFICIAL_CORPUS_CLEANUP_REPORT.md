# Official Corpus Cleanup Report

Дата (UTC): 2026-05-04T11:45:41Z

## Найденные source-папки

- `corpus/official/html/16`
- `corpus/official/html/17`
- `corpus/official/html/18`

Папки `official/html/{16,17,18}` в корне репозитория не найдены.

## Выполненные переносы

- `corpus/official/html/16` -> `corpus/postgres/html/16`
- `corpus/official/html/17` -> `corpus/postgres/html/17`
- `corpus/official/html/18` -> `corpus/postgres/html/18`

Целевые папки `corpus/postgres/html/{16,17,18}` до переноса отсутствовали, перезаписи существующей документации не было.

## Количество HTML-файлов в итоговой структуре

- `corpus/postgres/html/16`: **1167**
- `corpus/postgres/html/17`: **1141**
- `corpus/postgres/html/18`: **1146**

## Удалённые backup-файлы

Удалены только `download_manifest.jsonl.bak*` в разрешённых областях:

- `corpus/postgres/html/16/download_manifest.jsonl.bak`
- `corpus/postgres/html/16/download_manifest.jsonl.bak.20260429T144030Z`
- `corpus/postgres/html/17/download_manifest.jsonl.bak`
- `corpus/postgres/html/17/download_manifest.jsonl.bak.20260429T144041Z`
- `corpus/postgres/html/18/download_manifest.jsonl.bak`
- `corpus/postgres/html/18/download_manifest.jsonl.bak.20260429T144053Z`

Файлы `download_manifest.jsonl` не удалялись.

## Подтверждение по tutorial corpus

- `corpus/tutorial/**` в рамках этой операции не изменялся.

## Итоговая структура official corpus

```text
corpus/postgres/html/
├── 16/
├── 17/
└── 18/
```

Дополнительно: после переноса пустая legacy-папка `corpus/official/` была удалена как пустая.
