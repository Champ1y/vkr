# PostgreSQL Version-Aware RAG

Готовое веб-приложение на основе RAG для работы с документацией PostgreSQL с учётом major-версии.

Проект реализует:
- version-aware retrieval по официальной документации PostgreSQL;
- три режима ответа: `short`, `detailed`, `tutorial`;
- дополнительный учебный корпус (`supplementary`) как вспомогательный слой, не заменяющий official;
- трассировку источников до чанков;
- историю запросов с режимом, latency, источниками и score;
- локальный запуск через Docker Compose.
- индексацию official-корпуса из локальных HTML (`corpus/postgres/html/{16,17,18}`).

## Архитектура

Слои:
- `ingestion/indexing` (офлайн): загрузка документов, парсинг структуры, chunking с overlap, embeddings, запись в PostgreSQL + pgvector;
- `online pipeline`: валидация запроса, retrieval с фильтром версии и корпуса, reranking с приоритетом official, генерация итогового результата;
- `api/ui`: FastAPI endpoints + веб-интерфейс;
- `traceability`: `query_history` + `query_sources`.

Сервисы:
- `EmbeddingService` (local SentenceTransformer, `BAAI/bge-m3` в dense mode; hashing only for tests);
- `GenerationService` (Groq API, single provider);
- `RetrievalService`;
- `RerankingService`;
- `AskOrchestrationService`.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL + pgvector
- BeautifulSoup + httpx
- Docker Compose
- pytest

## Структура проекта

- `app/main.py` — FastAPI приложение
- `app/api/` — API роуты
- `app/db/` — модели и сессия БД
- `app/repositories/` — доступ к данным
- `app/services/` — бизнес-логика
- `app/services/ingestion/` — загрузка/парсинг/индексация
- `app/services/adapters/` — LLM/embedding адаптеры
- `app/web/` — UI шаблоны и статика
- `app/cli/manage.py` — CLI команды
- `alembic/` — миграции
- `corpus/tutorial/` — дополнительный учебный корпус
- `tests/` — unit/API тесты

## Переменные окружения

Скопируйте файл:

```bash
cp .env.example .env
```

Ключевые переменные:
- `DATABASE_URL`
- `SUPPORTED_PG_VERSIONS`
- `OFFICIAL_DOCS_BASE_URL` (используется для канонических source URL в БД)
- `CHUNK_SIZE`, `CHUNK_OVERLAP`
- `RETRIEVAL_TOP_K`, `RERANK_TOP_K`
- `EMBEDDING_DIMENSION`, `EMBEDDING_BATCH_SIZE`, `EMBEDDING_MAX_SEQ_LENGTH`
- `LLM_PROVIDER`, `LLM_MODEL`, `GROQ_API_KEY`, `GROQ_BASE_URL`
- `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`
- `SUPPLEMENTARY_DIR`
- `ADMIN_API_KEY`

## Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска:
- UI: `http://localhost:8000/`
- История: `http://localhost:8000/history`
- OpenAPI: `http://localhost:8000/docs`

Перед запуском generation-части обязательно задайте:
- `GROQ_API_KEY=<ваш ключ Groq>`
- `LLM_PROVIDER=groq`
- `LLM_MODEL=<доступная chat-модель Groq>`

### Запуск с Groq

1. Заполните `.env`:
   - `LLM_PROVIDER=groq`
   - `LLM_MODEL`
   - `GROQ_API_KEY`
   - `GROQ_BASE_URL=https://api.groq.com/openai/v1`
   - `EMBEDDING_PROVIDER=local`
   - `EMBEDDING_MODEL=BAAI/bge-m3`
   - `EMBEDDING_DIMENSION=1024`
   - `EMBEDDING_BATCH_SIZE=8`
   - `EMBEDDING_MAX_SEQ_LENGTH=8192`
2. Поднимите сервисы:

```bash
docker compose up --build
```

Если видите ошибку `Groq API key is not configured. Set GROQ_API_KEY.`:
1. Откройте `.env` и заполните `GROQ_API_KEY=<ваш_ключ>`.
2. Перезапустите контейнеры:
```bash
docker compose up -d --force-recreate backend
```

## Локальный запуск без Docker

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/python -m app.cli.manage seed-versions
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Миграции

```bash
.venv/bin/alembic upgrade head
```

## Индексация документации

### Через CLI

Индексация official корпуса для версии 16 (из локальной папки `corpus/postgres/html/16`):

```bash
.venv/bin/python -m app.cli.manage reindex --versions 16 --official
```

Индексация official + supplementary:

```bash
.venv/bin/python -m app.cli.manage reindex --versions 16 --official --supplementary
```

Безопасный вариант для long-running reindex с наблюдаемым прогрессом и короткими транзакциями:

```bash
.venv/bin/python -m app.cli.manage reindex \
  --versions 16 \
  --official \
  --supplementary \
  --batch-size 8 \
  --commit-every-docs 25 \
  --progress-every 10
```

### Проверка official manifest

```bash
python3 scripts/enrich_official_manifest.py
python3 scripts/validate_official_manifest.py
```

`enrich_official_manifest.py` нормализует metadata official corpus (title, content hash, license, version-aware source_url и др.) без изменения raw HTML.

`validate_official_manifest.py` проверяет, что version-aware `download_manifest.jsonl` не содержит плавающих `/docs/current/` ссылок, что `source_url` соответствует версии и что `content_hash` совпадает с локальными HTML.

### Полный reindex на BGE-M3 (16/17/18)

`BAAI/bge-m3` используется только в dense mode (pgvector). Sparse/ColBERT возможности BGE-M3 на текущем этапе не используются.

После смены embedding-модели нужно очистить/пересоздать старые embeddings и полностью переиндексировать corpus.

```bash
docker compose down
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python scripts/check_bge_m3_ready.py
docker compose run --rm backend python -m app.cli.manage seed-versions
docker compose run --rm backend python -m app.cli.manage reindex --versions 16 17 18 --official --supplementary
```

Для финального reindex не используйте `--max-pages`.

SQL-проверки после reindex:

```sql
SELECT embedding_model, embedding_dimension, count(*)
FROM embeddings
GROUP BY embedding_model, embedding_dimension;

SELECT v.major_version, d.corpus_type, count(*) AS documents
FROM documents d
JOIN versions v ON v.id = d.version_id
GROUP BY v.major_version, d.corpus_type
ORDER BY v.major_version, d.corpus_type;
```

### Через API

```http
POST /api/admin/reindex
X-Admin-Key: <ADMIN_API_KEY>
Content-Type: application/json

{
  "versions": ["16"],
  "include_official": true,
  "include_supplementary": true,
  "max_pages": 40
}
```

## Supplementary corpus

Папка:

- `corpus/tutorial`

Индексируются:
- `corpus/tutorial/curated/{16,17,18}/**/*.md`
- `corpus/tutorial/processed_html/**/*.md`

Не индексируются:
- `corpus/tutorial/html/**/*.html`
- `corpus/tutorial/external_registry/**`
- `corpus/tutorial/scripts/**`
- `corpus/tutorial/*REPORT*`
- `corpus/tutorial/*MANIFEST*`
- `corpus/tutorial/**/_backup*/**`
- `corpus/tutorial/**/__pycache__/**`
- `corpus/tutorial/**/*.pyc`

Индексация supplementary выполняется тем же пайплайном, но хранится как `corpus_type=supplementary`.

## API

### POST `/api/ask`

Request:

```json
{
  "question": "Как включить логическую репликацию?",
  "pg_version": "16",
  "answer_mode": "short"
}
```

Ответ `short` / `detailed`:

```json
{
  "answer_mode": "short",
  "pg_version": "16",
  "answer": "...",
  "sources": [
    {
      "title": "...",
      "url": "https://www.postgresql.org/docs/16/...",
      "corpus_type": "official",
      "source_role": "base",
      "section_path": "...",
      "rank_position": 1,
      "similarity_score": 0.91
    }
  ]
}
```

Ответ `tutorial`:

```json
{
  "answer_mode": "tutorial",
  "pg_version": "16",
  "tutorial": {
    "short_explanation": "...",
    "prerequisites": ["..."],
    "steps": ["..."],
    "notes": ["..."]
  },
  "sources": [
    {
      "title": "...",
      "url": "https://www.postgresql.org/docs/16/...",
      "corpus_type": "official",
      "source_role": "base",
      "section_path": "...",
      "rank_position": 1,
      "similarity_score": 0.92
    },
    {
      "title": "...",
      "url": "supplementary://curated/16/...",
      "corpus_type": "supplementary",
      "source_role": "supplementary",
      "section_path": "...",
      "rank_position": 2,
      "similarity_score": 0.75
    }
  ]
}
```

### GET `/api/versions`

Список поддерживаемых major-версий.

### GET `/api/health`

Проверка доступности API.

### GET `/api/health/embeddings`

Проверка embedding-конфига:
- активный provider;
- модель эмбеддингов;
- configured dimension;
- `max_seq_length`;
- `batch_size`;
- текущее окружение (`APP_ENV`).

### GET `/api/history`

История запросов с источниками и score.

## Логика режимов и корпусов

- `short` → только `official`
- `detailed` → только `official`
- `tutorial` → `official + supplementary`

Ограничения:
- supplementary не допускается в `short` и `detailed`;
- supplementary не заменяет official;
- version filter обязателен;
- URL источников берутся из реально найденных документов/чанков.

## Frontend

Frontend находится внутри backend-приложения:
- шаблоны: `app/web/templates/`
- статика: `app/web/static/`

Запуск UI:

```bash
docker compose up -d backend
```

После запуска:
- главная страница: `http://localhost:8000/`
- история запросов: `http://localhost:8000/history`

Проверка health:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/embeddings
# совместимый API-маршрут:
curl http://localhost:8000/api/health/embeddings
```

Логи backend:

```bash
docker compose logs --tail=100 backend
```

Важно: изменения frontend/UI не требуют reindex корпуса и не требуют пересчёта embeddings.

## Проверка Groq и embeddings

### Проверка Groq-конфига

Убедитесь, что в `.env` заполнены:

```bash
LLM_PROVIDER=groq
LLM_MODEL=...
GROQ_API_KEY=...
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### Важное разделение

- `EMBEDDING_PROVIDER=local` — это локальный провайдер embeddings для `BAAI/bge-m3` (retrieval).
- `LLM_PROVIDER=groq` — это генерация финального ответа через Groq API.
- Нельзя использовать `EMBEDDING_PROVIDER=groq`.
- Нельзя использовать любые другие значения `EMBEDDING_PROVIDER` в runtime кроме `local`.

### Проверка embedding-конфига

Проверьте endpoint:

```bash
curl http://localhost:8000/api/health/embeddings
```

`EMBEDDING_PROVIDER=hashing` предназначен только для автоматических тестов и не должен использоваться в development/production.

## Тесты

```bash
.venv/bin/python -m pytest -q
```

Покрыто:
- валидация `answer_mode/version`;
- правила выбора корпусов;
- запрет supplementary в `short`/`detailed`;
- возможность supplementary в `tutorial`;
- version guard для retrieval;
- базовые API тесты.

## Примечания по production-доработке

- добавить авторизацию/роли для admin endpoints;
- вынести длительный reindex в очередь задач;
- добавить метрики качества retrieval/reranking (nDCG, Recall@K);
- расширить e2e тесты с тестовой PostgreSQL в CI.
