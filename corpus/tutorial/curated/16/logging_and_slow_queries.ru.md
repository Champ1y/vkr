---
title: "Логи и медленные запросы в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "logging_and_slow_queries"
tags:
  - "logging"
  - "slow queries"
  - "log_min_duration_statement"
  - "EXPLAIN"
official_backing:
  - "https://www.postgresql.org/docs/16/runtime-config-logging.html"
  - "https://www.postgresql.org/docs/16/monitoring.html"
  - "https://www.postgresql.org/docs/16/sql-explain.html"
  - "https://www.postgresql.org/docs/16/using-explain.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Логи и медленные запросы в PostgreSQL 16

## Назначение

Объяснить, как найти медленные SQL-запросы через настройки логирования и перейти к анализу плана.

Этот файл написан для режима `tutorial` и особенно для `extended_mode=true`. Он не заменяет официальную документацию PostgreSQL 16, а помогает объяснять её проще и пошагово.

## Простое объяснение

Логи помогают найти, какие запросы медленные. `EXPLAIN` помогает понять, почему они медленные: как читаются таблицы, используются ли индексы и какой план выбрал PostgreSQL.

## Когда использовать

- медленные запросы;
- где смотреть логи;
- log_min_duration_statement;
- как включить логирование;
- как анализировать запрос;

## Предварительные условия

- есть доступ к настройкам сервера;
- понятно, что включение подробных логов может увеличить нагрузку;
- есть пример медленного SQL;

## Пошаговая инструкция

### Шаг 1. Проверить настройки логов

```sql
SHOW logging_collector;
SHOW log_directory;
SHOW log_filename;
SHOW log_min_duration_statement;
```

### Шаг 2. Временно установить порог медленных запросов

```sql
ALTER SYSTEM SET log_min_duration_statement = '500ms';
SELECT pg_reload_conf();
```

### Шаг 3. Проверить значение

```sql
SHOW log_min_duration_statement;
```

### Шаг 4. Взять SQL из логов и посмотреть план

```sql
EXPLAIN
SELECT * FROM orders WHERE customer_id = 10;
```

### Шаг 5. Если безопасно, посмотреть фактическое выполнение

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 10;
```

### Шаг 6. Проверить индексы

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'orders';
```

### Шаг 7. Обновить статистику

```sql
ANALYZE public.orders;
```

## Проверка результата

- медленный SQL найден в логах;
- `EXPLAIN` показывает план;
- после индекса или ANALYZE план и время сравниваются повторно;

## Типовые ошибки и как думать

### Включить логирование всех запросов в production

это может создать большой объём логов и нагрузку.

### Использовать `EXPLAIN ANALYZE` для UPDATE/DELETE без защиты

команда реально выполнится; для учебной проверки используй transaction и `ROLLBACK`.

### Считать любой `Seq Scan` плохим

для маленьких таблиц он может быть нормальным.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 16.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для поиска медленных запросов в PostgreSQL 16 проверь `log_min_duration_statement`, найди SQL в логах, выполни `EXPLAIN` или осторожно `EXPLAIN (ANALYZE, BUFFERS)`, затем проверь индексы и статистику.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 16. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Runtime Configuration / Logging`;
- `EXPLAIN`;
- `Using EXPLAIN`;
- `Monitoring Database Activity`;
