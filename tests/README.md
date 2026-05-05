# Тесты проекта

## Категории

- `unit` — unit-тесты без реальной БД/сети
- `api` — тесты FastAPI-эндпоинтов с моками
- `scenario` — сценарные тесты с мокнутым LLM
- `integration` — тесты с реальным PostgreSQL + pgvector

## Важно про integration

Integration-тесты используют **только отдельную тестовую БД** из `TEST_DATABASE_URL`.
Рабочая БД `rag_postgres` не должна использоваться.

Фикстуры integration-тестов:
- читают `TEST_DATABASE_URL` из окружения;
- создают extension `vector`;
- создают таблицы `Base.metadata.create_all`;
- после завершения удаляют таблицы `Base.metadata.drop_all`.

Если `TEST_DATABASE_URL` не задан, integration-тесты будут пропущены.

## Поднять тестовую БД

```bash
docker compose up -d postgres_test
```

## Запустить integration-тесты

```bash
TEST_DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5434/rag_postgres_test python -m pytest -m integration -q
```

## Запустить все тесты кроме integration

```bash
python -m pytest -m "not integration" -q
```
