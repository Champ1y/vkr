---
title: "Транзакции и базовые блокировки в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "transactions_and_locks_basics"
tags:
  - "transactions"
  - "locks"
  - "BEGIN"
  - "COMMIT"
  - "ROLLBACK"
  - "MVCC"
official_backing:
  - "https://www.postgresql.org/docs/17/tutorial-transactions.html"
  - "https://www.postgresql.org/docs/17/transaction-iso.html"
  - "https://www.postgresql.org/docs/17/explicit-locking.html"
  - "https://www.postgresql.org/docs/17/sql-begin.html"
  - "https://www.postgresql.org/docs/17/sql-commit.html"
  - "https://www.postgresql.org/docs/17/sql-rollback.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Транзакции и базовые блокировки в PostgreSQL 17

## Назначение

Этот материал помогает понять практическую основу транзакций и блокировок в PostgreSQL: как сохранить целостность данных и как диагностировать ожидания. Он нужен для ответов на вопросы "почему запрос ждёт", "что такое `idle in transaction`" и "как безопасно проектировать конкурентные обновления".

## Когда использовать

- операции должны выполняться атомарно (всё или ничего);
- есть конкурентные изменения одних и тех же строк;
- возникают ожидания, lock timeout или deadlock;
- нужно объяснить поведение `BEGIN`/`COMMIT`/`ROLLBACK`;
- требуется runbook для первичной диагностики блокировок.

## Простое объяснение

Транзакция объединяет несколько SQL-команд в одну логическую единицу. Пока транзакция не зафиксирована (`COMMIT`), другие участники могут не видеть изменения или ждать конфликтующие ресурсы. Если произошла ошибка, `ROLLBACK` отменяет изменения.

В PostgreSQL модель MVCC позволяет читать согласованные версии строк, но конфликтующие записи всё равно требуют синхронизации блокировками. Поэтому длинные транзакции опасны: они удерживают ресурсы, мешают vacuum и увеличивают latency у других запросов.

## Предварительные условия

- таблицы и ключи поддерживают корректные бизнес-операции;
- в приложении есть явные границы транзакций;
- настроены разумные таймауты (`lock_timeout`, `statement_timeout`) для production;
- есть доступ к `pg_stat_activity` и `pg_locks`;
- есть практика коротких транзакций без внешних сетевых ожиданий внутри.

## Минимальный рабочий пример

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

```sql
BEGIN;
INSERT INTO notes(title) VALUES ('temp row');
ROLLBACK;
```

```sql
SELECT a.pid, a.usename, a.state, a.wait_event_type, a.wait_event,
       l.locktype, l.mode, l.granted
FROM pg_stat_activity AS a
JOIN pg_locks AS l ON l.pid = a.pid
WHERE a.state <> 'idle';
```

## Пошаговый алгоритм

1. Определи границы транзакции вокруг бизнес-операции, которая должна быть атомарной.
2. Открой транзакцию через `BEGIN` и выполни минимально нужный набор SQL.
3. Избегай долгих вычислений и сетевых вызовов внутри открытой транзакции.
4. Фиксируй изменения через `COMMIT` или отменяй через `ROLLBACK` при ошибке.
5. При ожиданиях проверь `pg_stat_activity` и `pg_locks`.
6. Выяви blocking-сессию и контекст её запроса перед вмешательством.
7. При необходимости сокращай размер транзакций, меняй порядок операций или индексируй конфликтные запросы.
8. Повтори тест под конкурентной нагрузкой и убедись, что latency стабилизировалась.

## Как проверить результат

```sql
SELECT pid, usename, state, wait_event_type, wait_event,
       now() - xact_start AS xact_duration, query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY xact_duration DESC NULLS LAST;
```

```sql
SELECT locktype, mode, granted, relation::regclass AS relation_name, pid
FROM pg_locks
WHERE relation IS NOT NULL
ORDER BY relation_name, pid;
```

- транзакции завершаются быстро и не висят в `idle in transaction`;
- нет устойчивой очереди блокирующих ожиданий;
- целостность данных подтверждается после конкурентных операций;
- число инцидентов с lock wait снижается после изменений.

## Типовые ошибки

- Держать транзакцию открытой дольше, чем нужно.
- Выполнять долгие внешние операции внутри `BEGIN ... COMMIT`.
- Игнорировать `idle in transaction` в мониторинге.
- Смешивать много независимых задач в одну большую транзакцию.
- Пытаться лечить блокировки terminate-командами без анализа причины.

## Безопасность и ограничения

- Неправильные вмешательства в блокировки могут привести к каскадным ошибкам приложения.
- `EXPLAIN ANALYZE` на DML выполняет реальные изменения; тестируй осторожно.
- В production решения по cancel/terminate должны учитывать бизнес-критичность операций.
- Для сложных конфликтов нужно комбинировать анализ блокировок, индексов и изоляции транзакций.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/tutorial-transactions.html`
- `https://www.postgresql.org/docs/17/transaction-iso.html`
- `https://www.postgresql.org/docs/17/explicit-locking.html`
- `https://www.postgresql.org/docs/17/sql-begin.html`
- `https://www.postgresql.org/docs/17/sql-commit.html`
- `https://www.postgresql.org/docs/17/sql-rollback.html`

## Короткий вывод

Транзакции в PostgreSQL дают атомарность и согласованность, но требуют дисциплины: короткие операции, чёткие границы и быстрая фиксация. Блокировки нормальны при конкуренции, проблема начинается, когда они становятся длительными и непрозрачными. Практическая диагностика строится на `pg_stat_activity` и `pg_locks` с последующим устранением первопричины.
