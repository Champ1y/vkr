---
title: "Расширения PostgreSQL 17: CREATE EXTENSION и проверка"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "extensions_basics"
tags:
  - "extensions"
  - "CREATE EXTENSION"
  - "pg_extension"
  - "pgvector"
official_backing:
  - "https://www.postgresql.org/docs/17/extend-extensions.html"
  - "https://www.postgresql.org/docs/17/sql-createextension.html"
  - "https://www.postgresql.org/docs/17/catalog-pg-extension.html"
  - "https://www.postgresql.org/docs/17/view-pg-available-extensions.html"
  - "https://www.postgresql.org/docs/17/view-pg-available-extension-versions.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Расширения PostgreSQL 17: CREATE EXTENSION и проверка

## Назначение

Этот материал объясняет, как безопасно подключать и проверять расширения PostgreSQL в учебных и прикладных проектах. Он нужен, когда пользователь спрашивает, почему `CREATE EXTENSION` не работает, в какой базе создавать extension и как подтвердить результат.

## Когда использовать

- нужно добавить функциональность через extension (`vector`, `pg_stat_statements` и др.);
- база восстановлена из backup, и нужно проверить состав расширений;
- локальная среда и production ведут себя по-разному;
- требуется обновление версии extension;
- нужно подготовить миграцию с `CREATE EXTENSION IF NOT EXISTS`.

## Простое объяснение

Extension — это пакет SQL-объектов (иногда с бинарными компонентами), который PostgreSQL подключает в конкретной базе. Важно помнить две вещи. Первая: extension должен быть доступен серверу (на уровне установки PostgreSQL/ОС). Вторая: команда `CREATE EXTENSION` выполняется отдельно в каждой базе, где нужен функционал.

Для RAG-проектов типичный пример — extension `vector` (из `pgvector`). Если extension доступен серверу, команда создаёт типы, функции и операторы, после чего ими можно пользоваться в обычных SQL-запросах.

## Предварительные условия

- есть подключение к нужной базе через `psql`;
- у роли есть права на создание extension (или есть администратор, который выполнит команду);
- extension установлен на сервере и виден в `pg_available_extensions`;
- известно, в какой схеме должны появиться объекты;
- миграции согласованы между dev, stage и production.

## Минимальный рабочий пример

```sql
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('vector', 'pg_stat_statements')
ORDER BY name;

CREATE EXTENSION IF NOT EXISTS vector;

SELECT extname, extversion, extnamespace::regnamespace AS schema_name
FROM pg_extension
ORDER BY extname;
```

```text
\dx
```

## Пошаговый алгоритм

1. Подключись именно к той базе, где нужен extension.
2. Проверь доступность через `pg_available_extensions`.
3. Выполни `CREATE EXTENSION IF NOT EXISTS ...`.
4. Зафиксируй команду в миграции, чтобы окружения не расходились.
5. Убедись, что приложение использует тот же database и schema search path.
6. Для обновления версии extension используй отдельный этап с тестом (`ALTER EXTENSION ... UPDATE`).
7. Повтори проверку после деплоя на целевой среде.

## Как проверить результат

```sql
SELECT extname, extversion
FROM pg_extension
ORDER BY extname;
```

```sql
SELECT typname
FROM pg_type
WHERE typname = 'vector';
```

- `\dx` должен показывать установленный extension;
- `pg_extension` должен содержать ожидаемую версию;
- прикладной SQL, зависящий от extension, должен выполняться без ошибок "function/type does not exist".

## Типовые ошибки

- Выполнить `CREATE EXTENSION` не в той базе.
- Ожидать, что extension автоматически доступен во всех базах кластера.
- Иметь extension локально, но не иметь его в Docker/production.
- Путать имя пакета ОС и имя extension в SQL.
- Игнорировать различия версий extension между средами.

## Безопасность и ограничения

- Устанавливай extension только из доверенных источников и в контролируемом окружении.
- Некоторые extension добавляют нагрузку или меняют наблюдаемость, это надо учитывать заранее.
- Обновление extension может менять поведение функций; обязательно тестируй до production.
- Этот документ обучающий: точный список ограничений и совместимость версии сверяются по official docs 17.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/extend-extensions.html`
- `https://www.postgresql.org/docs/17/sql-createextension.html`
- `https://www.postgresql.org/docs/17/catalog-pg-extension.html`
- `https://www.postgresql.org/docs/17/view-pg-available-extensions.html`
- `https://www.postgresql.org/docs/17/view-pg-available-extension-versions.html`

## Короткий вывод

Extension в PostgreSQL подключается на уровне конкретной базы, поэтому ключевой риск — создать его "не там" или только в одной среде. Базовый цикл простой: проверить доступность, выполнить `CREATE EXTENSION IF NOT EXISTS`, подтвердить через `pg_extension` и закрепить в миграциях. Для фактических ограничений и совместимости всегда опирайся на official docs выбранной версии.
