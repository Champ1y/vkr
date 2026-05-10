# OLLAMA_REMOVAL_REPORT

## 1) Где были найдены упоминания Ollama (до правок)
По результатам аудита упоминания были в:
- `.env`
- `.env.backup`
- `app/services/adapters/ollama_client.py`

В runtime-файлах после правок (`.env`, `.env.example`, `docker-compose.yml`, `app/`) упоминаний Ollama нет.

## 2) Какие файлы изменены
Изменены:
- `.env`
- `.env.example`
- `app/core/config.py`
- `app/main.py`
- `app/services/adapters/embeddings.py`
- `app/services/adapters/generation.py`
- `app/web/static/app.js`
- `tests/test_bge_m3_migration.py`
- `tests/test_provider_rules.py`
- `README.md`
- `docs/BGE_M3_MIGRATION.md`

Удалены:
- `.env.backup`
- `app/services/adapters/ollama_client.py`

## 3) Финальная архитектура
Проект приведён к целевой архитектуре:
- Embeddings / retrieval: `EMBEDDING_PROVIDER=local`, `EMBEDDING_MODEL=BAAI/bge-m3`, `EMBEDDING_DIMENSION=1024`
- Vector storage: PostgreSQL + pgvector
- LLM generation: `LLM_PROVIDER=groq` + Groq API (`GROQ_API_KEY`, `LLM_MODEL`)

Поток:
1. Вопрос пользователя
2. Локальный `BAAI/bge-m3` строит embedding вопроса
3. PostgreSQL/pgvector ищет релевантные chunks
4. Контекст передаётся в Groq
5. Groq формирует финальный ответ

## 4) Что НЕ изменялось
- `corpus/`
- существующие embeddings в БД
- BAAI/bge-m3
- размерность embeddings (1024)
- reindex
- Alembic migrations
- PostgreSQL volume

## 5) Результаты проверок

### 5.1 Поиск Ollama
Команда:
```bash
grep -RIn "ollama\|OLLAMA" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=hf_cache --exclude-dir=logs --exclude-dir=__pycache__ || true
```
Результат: в runtime отсутствует; упоминания остаются только в этом отчёте как историческая фиксация выполненных изменений.

Дополнительно проверено по runtime-файлам:
```bash
grep -RIn "ollama\|OLLAMA" .env .env.example docker-compose.yml app || true
```
Результат: пусто.

### 5.2 Runtime env backend
Команда:
```bash
docker compose exec backend env | grep -E "EMBEDDING_PROVIDER|EMBEDDING_MODEL|EMBEDDING_DIMENSION|EMBEDDING_MAX_SEQ_LENGTH|LLM_PROVIDER|LLM_MODEL|GROQ_API_KEY|GROQ_BASE_URL|OLLAMA"
```
Фактически:
- `EMBEDDING_PROVIDER=local`
- `EMBEDDING_MODEL=BAAI/bge-m3`
- `EMBEDDING_DIMENSION=1024`
- `EMBEDDING_MAX_SEQ_LENGTH=8192`
- `LLM_PROVIDER=groq`
- `LLM_MODEL=llama-3.1-8b-instant`
- `GROQ_API_KEY` присутствует (значение скрыто)
- `OLLAMA*` отсутствуют

### 5.3 Health
Команды:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/embeddings
```
Результат:
- `/health`: `status=ok`
- `/health/embeddings`: `provider=local`, `model=BAAI/bge-m3`, `configured_dimension=1024`, `status=ok`

### 5.4 Проверка БД (read-only)
Команда:
```sql
SELECT embedding_model, embedding_dimension, count(*)
FROM embeddings
GROUP BY embedding_model, embedding_dimension;
```
Результат:
- `BAAI/bge-m3 | 1024 | 67919`

Команда:
```sql
SELECT v.major_version, d.corpus_type, count(*) AS documents
FROM documents d
JOIN versions v ON v.id = d.version_id
GROUP BY v.major_version, d.corpus_type
ORDER BY v.major_version, d.corpus_type;
```
Результат:
- 16: official/supplementary есть
- 17: official/supplementary есть
- 18: official/supplementary есть

### 5.5 Тесты
Команда из задания:
```bash
docker compose run --rm backend pytest
```
В этом окружении вернула import-path ошибку (`ModuleNotFoundError: No module named 'app'`).

Эквивалентный запуск, который корректно работает в контейнере:
```bash
docker compose run --rm backend python -m pytest
```
Результат: `78 passed, 3 skipped`.

### 5.6 Проверка preflight BGE-M3
Команда:
```bash
docker compose run --rm backend python scripts/check_bge_m3_ready.py
```
Результат:
- `BGE_M3_READY_FOR_REINDEX = true`
- sample embedding length = 1024
- DB checks = checked

## 6) Статус
- `OLLAMA_REMOVED_FROM_RUNTIME = true`
- `PROJECT_USES_GROQ_FOR_LLM = true`
- `PROJECT_USES_LOCAL_BGE_M3_FOR_EMBEDDINGS = true`
- `REINDEX_REQUIRED = false`
