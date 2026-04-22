# PostgreSQL Version-Aware RAG

Готовый прототип веб-приложения на основе RAG для работы с документацией PostgreSQL с учётом major-версии.

Проект реализует:
- version-aware retrieval по официальной документации PostgreSQL;
- два режима ответа: `answer` и `tutorial`;
- `extended_mode` только для `tutorial`;
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
- `EmbeddingService` (Ollama / OpenAI / hashing fallback);
- `GenerationService` (Groq OpenAI-compatible API, single provider);
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
- `data/supplementary/` — дополнительный учебный корпус
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
- `EMBEDDING_DIMENSION`
- `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_BASE_URL`
- `EMBEDDING_PROVIDER`, `OLLAMA_EMBEDDING_MODEL`
- `USE_OPENAI_EMBEDDINGS`, `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL`
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
- `GROQ_MODEL=<доступная chat-модель Groq>`

### Запуск с Groq

1. Заполните `.env`:
   - `GROQ_API_KEY`
   - `GROQ_MODEL`
   - `GROQ_BASE_URL=https://api.groq.com/openai/v1`
2. Поднимите сервисы:

```bash
docker compose up --build
```

Если видите ошибку `GROQ_API_KEY не задан`:
1. Откройте `.env` и заполните `GROQ_API_KEY=<ваш_ключ>`.
2. Перезапустите контейнеры:
```bash
docker compose down
docker compose up --build
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

- `data/supplementary/<major_version>/...`

Поддерживаются файлы:
- `.md`
- `.txt`
- `.html`

Пример:
- `data/supplementary/16/logical_replication_basics.md`

Индексация supplementary выполняется тем же пайплайном, но хранится как `corpus_type=supplementary`.

## API

### POST `/api/ask`

Request:

```json
{
  "question": "Как включить логическую репликацию?",
  "pg_version": "16",
  "mode": "answer",
  "extended_mode": false
}
```

Ответ `answer`:

```json
{
  "mode": "answer",
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
  "mode": "tutorial",
  "pg_version": "16",
  "extended_mode": true,
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
      "url": "supplementary://16/...",
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

### GET `/api/history`

История запросов с источниками и score.

## Логика режимов и корпусов

- `answer` → только `official`
- `tutorial` + `extended_mode=false` → только `official`
- `tutorial` + `extended_mode=true` → `official + supplementary`

Ограничения:
- supplementary не допускается в `answer`;
- supplementary не заменяет official;
- version filter обязателен;
- URL источников берутся из реально найденных документов/чанков.

## Проверка Ollama

Generation использует Groq. Ollama нужен только если embeddings идут через `EMBEDDING_PROVIDER=ollama`.

### Проверка Groq-конфига

Убедитесь, что в `.env` заполнены:

```bash
GROQ_API_KEY=...
GROQ_MODEL=...
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### Проверка Ollama (только для embeddings)

Проверить доступность сервера Ollama:

```bash
curl http://localhost:11434/api/tags
```

Проверить, что модели загружены:

```bash
ollama list
```

Загрузить embedding-модель (если используется Ollama для embeddings):

```bash
ollama pull nomic-embed-text
```

## Тесты

```bash
.venv/bin/python -m pytest -q
```

Покрыто:
- валидация `mode/version/extended_mode`;
- правила выбора корпусов;
- запрет supplementary в `answer`;
- возможность supplementary в `tutorial + extended_mode=true`;
- version guard для retrieval;
- базовые API тесты.

## Примечания по production-доработке

- добавить авторизацию/роли для admin endpoints;
- вынести длительный reindex в очередь задач;
- добавить метрики качества retrieval/reranking (nDCG, Recall@K);
- расширить e2e тесты с тестовой PostgreSQL в CI.
