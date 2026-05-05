---
title: "Оконные функции в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "window_functions_basics"
tags:
  - "window functions"
  - "OVER"
  - "PARTITION BY"
  - "analytics"
official_backing:
  - "https://www.postgresql.org/docs/18/tutorial-window.html"
  - "https://www.postgresql.org/docs/18/functions-window.html"
external_reference:
  - "https://www.crunchydata.com/developers/tutorials"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Оконные функции в PostgreSQL 18

## Назначение

Этот материал учит применять window functions для аналитики без потери детализации строк. Он закрывает типовые задачи ranking, сравнения с предыдущей строкой и расчёта накопительных показателей.

## Когда использовать

- нужно посчитать номер строки в группе (`row_number()`);
- требуется ранжирование (`rank()`, `dense_rank()`);
- нужно сравнить текущую строку с предыдущей/следующей (`lag()`, `lead()`);
- требуется накопительная сумма по времени;
- важно сохранить исходные строки, а не схлопывать их как при `GROUP BY`.

## Простое объяснение

`GROUP BY` агрегирует данные и уменьшает число строк: одна группа — одна строка. Window functions делают расчёт "поверх окна", но оставляют каждую исходную строку в результате. Поэтому можно одновременно видеть строку и её аналитические показатели.

Синтаксическая основа — `OVER (...)`. Внутри окна обычно задают:
- `PARTITION BY` — разделение строк на независимые группы;
- `ORDER BY` — порядок внутри каждой группы;
- при необходимости frame (границы окна), который влияет на running-расчёты.

Для ранжирования и сравнения строк важен корректный `ORDER BY`. Если порядок не задан или задан неоднозначно, результат может быть непредсказуемым для бизнес-аналитики.

## Предварительные условия

- есть таблица с колонками, по которым понятны группа и порядок;
- определены критерии сортировки при равных значениях;
- данные очищены от неожиданных `NULL`, если это важно для расчёта;
- есть тестовые наборы для проверки ожидаемой аналитики;
- понятно, что window functions могут требовать сортировки и влиять на производительность.

## Минимальный рабочий пример

```sql
SELECT customer_id,
       created_at,
       amount,
       row_number() OVER (
         PARTITION BY customer_id
         ORDER BY created_at
       ) AS rn,
       rank() OVER (
         PARTITION BY customer_id
         ORDER BY amount DESC
       ) AS rnk,
       dense_rank() OVER (
         PARTITION BY customer_id
         ORDER BY amount DESC
       ) AS drnk,
       lag(amount) OVER (
         PARTITION BY customer_id
         ORDER BY created_at
       ) AS prev_amount,
       lead(amount) OVER (
         PARTITION BY customer_id
         ORDER BY created_at
       ) AS next_amount,
       sum(amount) OVER (
         PARTITION BY customer_id
         ORDER BY created_at
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM sales;
```

## Пошаговый алгоритм

1. Определи, чем `PARTITION BY` разделяет данные (например, `customer_id`).
2. Выбери детерминированный `ORDER BY` внутри окна (дата + tie-breaker).
3. Добавь `row_number()` для последовательной нумерации в группе.
4. Для рейтинга по значению добавь `rank()` или `dense_rank()`.
5. Для сравнения соседних записей используй `lag()`/`lead()`.
6. Для накопительного показателя используй `sum() OVER (...)` с явным frame.
7. Сверь результат на небольшом наборе строк вручную.
8. После этого проверяй план и производительность на полном объёме.

## Как проверить результат

```sql
SELECT customer_id, created_at, amount,
       row_number() OVER (PARTITION BY customer_id ORDER BY created_at) AS rn
FROM sales
ORDER BY customer_id, created_at;
```

```sql
SELECT customer_id, created_at, amount,
       sum(amount) OVER (
         PARTITION BY customer_id
         ORDER BY created_at
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM sales
ORDER BY customer_id, created_at;
```

```sql
SELECT customer_id, amount,
       rank() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rnk,
       dense_rank() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS drnk
FROM sales
ORDER BY customer_id, amount DESC;
```

- нумерация и ранги должны совпадать с ручной проверкой на sample-данных;
- running total должен возрастать по выбранному порядку;
- `lag()`/`lead()` должны ссылаться на ожидаемые соседние строки.

## Типовые ошибки

- Путать `GROUP BY` и window functions.
- Не задавать `ORDER BY` в `OVER`, когда порядок критичен.
- Использовать неоднозначный порядок и получать нестабильный результат.
- Забывать о frame для running-агрегатов и удивляться значению.
- Проверять только синтаксис, но не сверять бизнес-логику расчёта.

## Безопасность и ограничения

- Сложные оконные расчёты могут требовать сортировки и памяти; проверяй их на реальном объёме.
- Ошибка в `ORDER BY` и frame приводит не к ошибке SQL, а к логически неверной аналитике.
- Для production-отчётов всегда фиксируй критерии сортировки и обновления данных.
- Этот материал учебный; детали функций и edge-cases уточняй в official docs.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/18/tutorial-window.html`
- `https://www.postgresql.org/docs/18/functions-window.html`

## Короткий вывод

Window functions дают аналитические расчёты по строкам без потери детализации, в отличие от `GROUP BY`. Ключ к корректному результату — правильно задать `OVER`, `PARTITION BY`, `ORDER BY` и frame. Для практики особенно важны `row_number()`, `rank()`, `dense_rank()`, `lag()`, `lead()` и `sum() OVER`.
