# BGE M3 Migration Report

## 1) Изменённые файлы

- `.env`
- `.env.example`
- `.gitignore`
- `README.md`
- `docs/BGE_M3_MIGRATION.md`
- `app/core/config.py`
- `app/services/adapters/embeddings.py`
- `app/services/ingestion/supplementary_loader.py`
- `app/api/routes/health.py`
- `app/schemas/common.py`
- `app/main.py`
- `alembic/versions/20260401_0001_initial.py`
- `alembic/versions/20260504_0002_bge_m3_1024.py`
- `scripts/check_bge_m3_ready.py`
- `tests/test_api.py`
- `tests/test_bge_m3_migration.py`

## 2) Текущая embedding-конфигурация

- `EMBEDDING_MODEL=BAAI/bge-m3`
- `EMBEDDING_DIMENSION=1024`
- `EMBEDDING_BATCH_SIZE=8`
- `EMBEDDING_MAX_SEQ_LENGTH=8192`
- `EMBEDDING_PROVIDER=local`

Дополнительно:

- Используется только dense mode через pgvector.
- Sparse/ColBERT возможности BGE-M3 не включались.
- После смены модели требуется очистка старых индексов и полный reindex.

## 3) Как исправлен supplementary loader

- Loader переведён на чтение из `settings.supplementary_path`.
- По умолчанию используется `corpus/tutorial`.
- Для каждой версии загружается:
  - `curated/{version}/**/*.md`
  - `processed_html/**/*.md`
- Реализован парсинг YAML front matter.
- `curated`:
  - `title` из YAML, fallback на первый heading.
  - `source_url` в формате `supplementary://curated/{version}/{relative_path}`.
  - embedding `text` формируется из body без front matter.
  - при `pg_version` mismatch файл пропускается с warning.
- `processed_html`:
  - `title` из YAML.
  - `source_url` из YAML.
  - индексируется только при `indexable: true`.
  - embedding `text` формируется из body без front matter.
- Старый supplementary layout удалён из загрузчика; текущий supplementary path — `corpus/tutorial`.

## 4) Текущий supplementary path

- `SUPPLEMENTARY_DIR=corpus/tutorial`

## 5) DB schema / Alembic

- `20260401_0001_initial.py`: default dimension изменён на `1024`.
- Добавлена миграция `20260504_0002_bge_m3_1024.py`:
  - `CREATE EXTENSION IF NOT EXISTS vector`
  - `TRUNCATE TABLE documents CASCADE`
  - `ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector(1024)`
- Downgrade:
  - `TRUNCATE TABLE documents CASCADE`
  - `ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector(768)`

Примечание: миграция destructive для индексируемых данных и требует полного reindex.

## 6) Команды migration + reindex

```bash
docker compose down
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python scripts/check_bge_m3_ready.py
docker compose run --rm backend python -m app.cli.manage seed-versions
docker compose run --rm backend python -m app.cli.manage reindex --versions 16 17 18 --official --supplementary
```

Важно: для финального reindex не использовать `--max-pages`.

## 7) Что проверяет scripts/check_bge_m3_ready.py

- `embedding_model == BAAI/bge-m3`
- `embedding_dimension == 1024`
- корректность `SUPPLEMENTARY_DIR` (ожидается `corpus/tutorial`)
- запуск corpus validator и наличие `CORPUS_READY_FOR_CHUNKING_AND_EMBEDDINGS = true`
- наличие `vector` extension в БД
- тип `embeddings.embedding` как `vector(1024)`
- sample embedding длины `1024`
- что supplementary loader для версии `16` загружает значительно больше 2 документов
- явный статус DB-проверок (`checked`/`not_checked`)

## 8) Статус

- `READY_TO_RUN_BGE_M3_REINDEX = false`

Причина текущего false в локальном запуске `python3 scripts/check_bge_m3_ready.py`:

- отсутствуют python-зависимости приложения в системном интерпретаторе (`pydantic`), поэтому preflight не может завершить полный runtime-check.

## Дополнительно

- `.env` добавлен в `.gitignore`; его не нужно включать в git/archive.
- Очистка `__pycache__/pyc` выполнена в `app/`, `tests/`, `alembic/`.
- Не удалось удалить `scripts/__pycache__/*` из-за прав доступа на директорию/файлы.
