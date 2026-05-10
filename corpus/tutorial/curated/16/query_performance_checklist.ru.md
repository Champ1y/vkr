---
title: "Checklist диагностики медленного запроса в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "query_performance_checklist"
tags:
  - "performance"
  - "slow query"
  - "EXPLAIN"
  - "statistics"
  - "indexes"
official_backing:
  - "https://www.postgresql.org/docs/16/using-explain.html"
  - "https://www.postgresql.org/docs/16/sql-explain.html"
  - "https://www.postgresql.org/docs/16/monitoring-stats.html"
  - "https://www.postgresql.org/docs/16/indexes-examine.html"
  - "https://www.postgresql.org/docs/16/routine-vacuuming.html"
external_reference:
  - "https://wiki.postgresql.org/wiki/SlowQueryQuestions"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Checklist диагностики медленного запроса в PostgreSQL 16

## Назначение

Этот checklist нужен для системной диагностики медленных SQL-запросов: от сбора фактов до проверки результата после изменений. Он особенно полезен в RAG-режиме, когда требуется дать пользователю не "совет по ощущениям", а воспроизводимый и безопасный алгоритм.

## Когда использовать

- endpoint или отчёт стал заметно медленнее;
- появились жалобы на таймауты и долгие транзакции;
- непонятно, проблема в SQL, статистике, индексах или блокировках;
- нужно доказать, что оптимизация реально помогла;
- требуется повторяемый runbook для команды.

## Простое объяснение

Производительность запроса в PostgreSQL почти всегда зависит от трёх вещей: планировщик, данные и конкуренция за ресурсы. Планировщик выбирает план по статистике. Если статистика устарела, выбирается неоптимальный путь. Даже хороший план может замедляться из-за блокировок, I/O или конкурирующих запросов.

Поэтому диагностика строится вокруг фактов: точный SQL, `EXPLAIN (ANALYZE, BUFFERS)`, состояние таблиц и индексов, текущая активность в `pg_stat_activity`. Изменять сразу всё подряд (индексы, параметры, vacuum) опасно: после такого сложно понять, что действительно сработало.

## Предварительные условия

- есть проблемный SQL в исходном виде (с реальными фильтрами);
- известно, где замеряли время (приложение, `psql`, job);
- есть доступ к `pg_stat_activity` и описанию таблиц (`\d`);
- есть безопасная среда для проверки гипотез;
- есть baseline: исходная длительность и частота запроса.

## Минимальный рабочий пример

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42
ORDER BY created_at DESC
LIMIT 50;
```

```sql
ANALYZE public.orders;
```

```sql
SELECT pid, state, wait_event_type, wait_event, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY duration DESC;
```

## Пошаговый алгоритм

1. Зафиксируй SQL и контекст выполнения: параметры, время, частоту, важность для пользователя.
2. Сними текущий план через `EXPLAIN (ANALYZE, BUFFERS)` и сохрани как baseline.
3. Проверь структуру таблиц и индексов (`\d`, `\d+`), чтобы увидеть реальное покрытие запроса.
4. Сравни `estimated rows` и `actual rows`: большие расхождения часто указывают на проблемы статистики.
5. При необходимости обнови статистику (`ANALYZE`) и повтори измерение.
6. Проверь конкуренцию: активные запросы, блокировки, долгие транзакции, `idle in transaction`.
7. Сформируй одну гипотезу за раз (например, новый индекс, переписывание условия, изменение join-order).
8. Применяй изменение в тестовой среде, снова измеряй `EXPLAIN (ANALYZE, BUFFERS)` и сравни с baseline.
9. Только после подтверждения эффекта переноси изменение в production через контролируемый деплой.

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
SELECT relname, n_live_tup, n_dead_tup, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'orders';
```

```sql
SELECT pid, wait_event_type, wait_event, state, now() - query_start AS duration
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY duration DESC;
```

- фактическое время запроса уменьшилось в сопоставимых условиях;
- план стал проще или дешевле по I/O/CPU;
- нет роста блокировок и деградации соседних операций;
- улучшение подтверждается на повторных запусках, а не на единичном замере.

## Типовые ошибки

- Смотреть только `EXPLAIN` без `ANALYZE` и принимать решения по теории.
- Оптимизировать "вслепую", не сохранив исходный baseline.
- Добавлять много индексов сразу и терять причинно-следственную связь.
- Игнорировать блокировки и ожидания, когда проблема не в плане.
- Делать вывод по одному запуску без повторяемости.

## Безопасность и ограничения

- `EXPLAIN ANALYZE` реально выполняет запрос: для `UPDATE/DELETE` используй осторожный подход (например, тестовая среда или транзакция с `ROLLBACK`).
- Индексные и конфигурационные изменения в production должны проходить через change window.
- Чрезмерная оптимизация одного запроса может ухудшить общий workload.
- Этот checklist учебный: детальные гарантии поведения конкретных операторов сверяются по official docs версии 16.

## Что искать в official corpus

- `https://www.postgresql.org/docs/16/using-explain.html`
- `https://www.postgresql.org/docs/16/sql-explain.html`
- `https://www.postgresql.org/docs/16/monitoring-stats.html`
- `https://www.postgresql.org/docs/16/indexes-examine.html`
- `https://www.postgresql.org/docs/16/routine-vacuuming.html`

## Короткий вывод

Ускорение запроса начинается с фактов: точный SQL, baseline и `EXPLAIN (ANALYZE, BUFFERS)`. Дальше идёт пошаговая проверка статистики, индексов и конкурентной нагрузки, по одной гипотезе за раз. Улучшение считается реальным только если оно повторяемо и не ломает соседние сценарии.
