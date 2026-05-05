---
title: "EXPLAIN и индексы в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "explain_and_indexes"
tags:
  - "EXPLAIN"
  - "indexes"
  - "query plan"
  - "CREATE INDEX"
official_backing:
  - "https://www.postgresql.org/docs/18/sql-explain.html"
  - "https://www.postgresql.org/docs/18/using-explain.html"
  - "https://www.postgresql.org/docs/18/indexes.html"
  - "https://www.postgresql.org/docs/18/sql-createindex.html"
  - "https://www.postgresql.org/docs/18/indexes-types.html"
  - "https://www.postgresql.org/docs/18/indexes-multicolumn.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# EXPLAIN и индексы в PostgreSQL 18

## Назначение

Научить читать базовые планы выполнения и понимать, когда индекс помогает.

Этот файл написан для режима `tutorial` и особенно для `extended_mode=true`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

PostgreSQL сначала строит план выполнения запроса. `EXPLAIN` показывает план, а индекс помогает быстро находить строки по условиям, но занимает место и замедляет изменение данных.

## Когда использовать

- как читать EXPLAIN;
- Seq Scan;
- Index Scan;
- как создать индекс;
- почему индекс не используется;

## Предварительные условия

- есть конкретный SQL-запрос;
- известна таблица и фильтры;
- есть право создавать индекс или хотя бы читать план;

## Пошаговая инструкция

### Шаг 1. Посмотреть план без выполнения

```sql
EXPLAIN
SELECT * FROM orders WHERE customer_id = 10;
```

### Шаг 2. Посмотреть реальное выполнение

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 10;
```

### Шаг 3. Создать индекс под фильтр

```sql
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
```

### Шаг 4. Создать индекс под фильтр и сортировку

```sql
CREATE INDEX orders_customer_created_idx ON orders (customer_id, created_at DESC);
```

### Шаг 5. Посмотреть индексы

```sql
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'orders';
```

### Шаг 6. Обновить статистику

```sql
ANALYZE orders;
```

## Проверка результата

- план до и после индекса сравнивается;
- индекс соответствует WHERE/JOIN/ORDER BY;
- после массовых изменений выполнен `ANALYZE`;
- учтено влияние индекса на запись;

## Типовые ошибки и как думать

### Создавать индекс на каждую колонку

индексы нужны под реальные частые запросы.

### Думать, что индекс всегда ускоряет

если возвращается большая часть таблицы, `Seq Scan` может быть быстрее.

### Игнорировать actual rows

большое расхождение estimated/actual rows указывает на проблему статистики или распределения данных.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для анализа запроса в PostgreSQL 18 используй `EXPLAIN`, затем при необходимости `EXPLAIN (ANALYZE, BUFFERS)`. Индекс создавай под конкретный частый фильтр, join или сортировку и проверяй план повторно.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `EXPLAIN`;
- `Using EXPLAIN`;
- `Indexes`;
- `CREATE INDEX`;
- `Multicolumn Indexes`;
