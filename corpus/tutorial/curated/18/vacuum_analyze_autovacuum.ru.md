---
title: "VACUUM, ANALYZE и autovacuum в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "vacuum_analyze_autovacuum"
tags:
  - "VACUUM"
  - "ANALYZE"
  - "autovacuum"
  - "maintenance"
official_backing:
  - "https://www.postgresql.org/docs/18/routine-vacuuming.html"
  - "https://www.postgresql.org/docs/18/sql-vacuum.html"
  - "https://www.postgresql.org/docs/18/sql-analyze.html"
  - "https://www.postgresql.org/docs/18/runtime-config-vacuum.html"
  - "https://www.postgresql.org/docs/18/monitoring-stats.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# VACUUM, ANALYZE и autovacuum в PostgreSQL 18

## Назначение

Объяснить, зачем PostgreSQL нужны обслуживание таблиц, очистка dead tuples и статистика планировщика.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

Из-за MVCC старые версии строк не исчезают сразу после UPDATE/DELETE. `VACUUM` помогает очищать dead tuples и переиспользовать место. `ANALYZE` обновляет статистику для планировщика. Autovacuum автоматизирует эти операции.

## Когда использовать

- зачем VACUUM;
- что такое autovacuum;
- база растёт;
- после загрузки данных медленные запросы;
- когда ANALYZE;

## Предварительные условия

- понятно, какая таблица активно меняется;
- есть право выполнять VACUUM/ANALYZE;
- известно, есть ли autovacuum;

## Пошаговая инструкция

### Шаг 1. Проверить autovacuum

```sql
SHOW autovacuum;
SHOW autovacuum_max_workers;
SHOW autovacuum_naptime;
```

### Шаг 2. Найти таблицы с dead tuples

```sql
SELECT relname, n_live_tup, n_dead_tup, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Шаг 3. Выполнить обслуживание конкретной таблицы

```sql
VACUUM ANALYZE public.orders;
```

### Шаг 4. После массовой загрузки обновить статистику

```sql
ANALYZE public.orders;
```

### Шаг 5. Проверить прогресс vacuum

```sql
SELECT * FROM pg_stat_progress_vacuum;
```

## Проверка результата

- autovacuum включён;
- `n_dead_tup` контролируется;
- после большой загрузки выполнен `ANALYZE`;
- `VACUUM FULL` не используется как обычная ежедневная операция;

## Типовые ошибки и как думать

### Отключить autovacuum

обычно это приводит к bloat, устаревшей статистике и рискам wraparound.

### Часто запускать `VACUUM FULL`

он переписывает таблицу и требует сильную блокировку.

### Ожидать, что обычный VACUUM вернёт место ОС

обычно он делает место доступным для переиспользования внутри PostgreSQL.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

В PostgreSQL 18 `VACUUM` очищает dead tuples, `ANALYZE` обновляет статистику, а autovacuum делает это автоматически. Не отключай autovacuum без серьёзной причины и не используй `VACUUM FULL` как обычную регулярную операцию.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Routine Vacuuming`;
- `VACUUM`;
- `ANALYZE`;
- `Autovacuum`;
- `pg_stat_user_tables`;
