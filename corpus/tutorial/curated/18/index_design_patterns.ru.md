---
title: "Практические шаблоны проектирования индексов в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "index_design_patterns"
tags:
  - "index design"
  - "btree"
  - "partial index"
  - "expression index"
  - "multicolumn index"
official_backing:
  - "https://www.postgresql.org/docs/18/indexes.html"
  - "https://www.postgresql.org/docs/18/indexes-types.html"
  - "https://www.postgresql.org/docs/18/indexes-multicolumn.html"
  - "https://www.postgresql.org/docs/18/indexes-partial.html"
  - "https://www.postgresql.org/docs/18/indexes-expressional.html"
  - "https://www.postgresql.org/docs/18/sql-createindex.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Практические шаблоны проектирования индексов в PostgreSQL 18

## Назначение

Этот материал даёт практический способ выбирать и проверять индексы под реальные запросы, а не "на всякий случай". Он закрывает вопросы вида: какой индекс нужен для `WHERE + ORDER BY`, когда уместен partial index и почему после создания индекса запрос иногда не ускорился.

## Когда использовать

- запрос стабильно медленный и есть план `EXPLAIN`;
- таблица выросла, а старые индексы перестали помогать;
- нужно ускорить фильтрацию, join или сортировку;
- нужно уменьшить число "лишних" индексов, мешающих записи;
- требуется подготовить индексную стратегию перед релизом.

## Простое объяснение

Индекс — это компромисс между скоростью чтения и стоимостью записи. Он помогает быстро находить строки, но каждый `INSERT/UPDATE/DELETE` должен обновлять индексные структуры. Поэтому задача не в максимальном числе индексов, а в точном покрытии частых запросов.

В PostgreSQL базовый тип — B-tree. Он хорошо работает для сравнений, диапазонов и сортировок. Multi-column индекс чувствителен к порядку колонок: сначала ставят более селективные или часто используемые в `WHERE` поля, а затем поля сортировки. Partial index хорош, когда запросы регулярно работают только по части данных (например, `status = 'active'`). Expression index работает, когда фильтр использует выражение (`lower(email)`).

## Предварительные условия

- есть конкретный SQL-запрос и его частота/важность;
- есть `EXPLAIN (ANALYZE, BUFFERS)` до изменений;
- понятна доля чтений и записей в таблице;
- статистика таблиц актуальна (`ANALYZE` выполнен);
- изменение можно протестировать на безопасной среде.

## Минимальный рабочий пример

```sql
CREATE INDEX IF NOT EXISTS orders_customer_id_idx
ON orders (customer_id);

CREATE INDEX IF NOT EXISTS orders_customer_created_idx
ON orders (customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS orders_active_created_idx
ON orders (created_at DESC)
WHERE status = 'active';

CREATE INDEX IF NOT EXISTS users_lower_email_idx
ON users (lower(email));
```

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42
ORDER BY created_at DESC
LIMIT 50;
```

## Пошаговый алгоритм

1. Выбери один проблемный запрос, который действительно важен для пользователя.
2. Разбери `WHERE`, `JOIN`, `ORDER BY`, `LIMIT` и частоту выполнения.
3. Сопоставь паттерн запроса с типом индекса (обычно B-tree, иногда partial/expression).
4. Создай минимально необходимый индекс и избегай дублирования существующих.
5. Повтори `EXPLAIN (ANALYZE, BUFFERS)` и сравни план, время и I/O.
6. Проверь влияние на записи (latency `INSERT/UPDATE/DELETE`).
7. Удали или не добавляй индексы, которые не используются.

## Как проверить результат

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42
ORDER BY created_at DESC
LIMIT 50;
```

```sql
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE relname = 'orders'
ORDER BY idx_scan DESC;
```

- в плане должен появиться ожидаемый `Index Scan`/`Bitmap Index Scan`;
- фактическое время выполнения и чтения буферов должны снизиться;
- `idx_scan` для целевого индекса должен расти на реальном workload.

## Типовые ошибки

- Создавать индекс на каждую колонку без сценария использования.
- Неправильно выбирать порядок колонок в multi-column индексе.
- Делать partial index, но писать запрос без условия partial-предиката.
- Создать expression index и забыть то же выражение в `WHERE`.
- Проверять только создание индекса, но не проверять план и фактическую нагрузку.

## Безопасность и ограничения

- `CREATE INDEX` на нагруженной таблице может блокировать запись; для online-сценариев анализируй `CREATE INDEX CONCURRENTLY`.
- Любой новый индекс увеличивает размер данных и стоимость операций записи.
- `EXPLAIN ANALYZE` запускает запрос реально, поэтому осторожно с тяжёлыми запросами и DML.
- Этот материал не заменяет official guidance по типам индексов и ограничениям их применения.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/18/indexes.html`
- `https://www.postgresql.org/docs/18/indexes-types.html`
- `https://www.postgresql.org/docs/18/indexes-multicolumn.html`
- `https://www.postgresql.org/docs/18/indexes-partial.html`
- `https://www.postgresql.org/docs/18/indexes-expressional.html`
- `https://www.postgresql.org/docs/18/sql-createindex.html`

## Короткий вывод

Индекс в PostgreSQL проектируют от конкретного запроса и подтверждают через `EXPLAIN (ANALYZE, BUFFERS)`. Полезнее один точный индекс, чем набор дублирующих. После ускорения чтения обязательно проверяют цену этого решения на запись и сопровождаемость схемы.
