---
title: "Практические SQL-задачи для PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial_practice"
topic: "sql_practice_tasks"
tags:
  - "SQL practice"
  - "SELECT"
  - "JOIN"
  - "GROUP BY"
  - "HAVING"
  - "window functions"
official_backing:
  - "https://www.postgresql.org/docs/18/tutorial-select.html"
  - "https://www.postgresql.org/docs/18/tutorial-join.html"
  - "https://www.postgresql.org/docs/18/tutorial-agg.html"
  - "https://www.postgresql.org/docs/18/tutorial-window.html"
external_reference:
  - "https://pgexercises.com/"
  - "https://pgexercises.com/questions/basic/"
  - "https://pgexercises.com/questions/joins/"
  - "https://pgexercises.com/questions/aggregates/"
usage_rule: "Использовать как учебный practice-layer. Проверка фактов и синтаксиса должна опираться на official corpus выбранной версии."
---

# Практические SQL-задачи для PostgreSQL 18

## Назначение

Этот файл закрывает практический слой обучающего режима: пользователь не только читает объяснение, но и получает задания для самостоятельного выполнения.

## Подготовка учебных таблиц

```sql
CREATE TABLE customers (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    city text NOT NULL
);

CREATE TABLE orders (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES customers(id),
    total numeric(10,2) NOT NULL,
    created_at date NOT NULL
);

INSERT INTO customers(name, city) VALUES
('Alice', 'Moscow'),
('Bob', 'Kazan'),
('Charlie', 'Moscow');

INSERT INTO orders(customer_id, total, created_at) VALUES
(1, 100.00, '2026-01-10'),
(1, 250.00, '2026-01-15'),
(2, 90.00, '2026-02-01'),
(3, 500.00, '2026-02-03');
```

## Задачи уровня 1: SELECT и WHERE

1. Вывести всех клиентов.
2. Вывести клиентов из города `Moscow`.
3. Вывести заказы дороже `100`.
4. Отсортировать заказы по сумме по убыванию.

## Задачи уровня 2: JOIN

1. Вывести имя клиента и сумму каждого заказа.
2. Вывести только заказы клиентов из `Moscow`.
3. Найти клиентов, у которых есть хотя бы один заказ.
4. Вывести клиентов и заказы так, чтобы клиенты без заказов тоже были видны.

## Задачи уровня 3: GROUP BY и HAVING

1. Посчитать сумму заказов по каждому клиенту.
2. Посчитать количество заказов по каждому клиенту.
3. Найти клиентов, у которых сумма заказов больше `200`.
4. Посчитать сумму заказов по городам.

## Задачи уровня 4: оконные функции

1. Пронумеровать заказы каждого клиента по дате.
2. Посчитать накопительную сумму заказов по каждому клиенту.
3. Найти самый дорогой заказ каждого клиента.

## Проверочные решения

### Сумма заказов по клиентам

```sql
SELECT c.name, sum(o.total) AS total_sum
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name
ORDER BY total_sum DESC;
```

### Клиенты с суммой заказов больше 200

```sql
SELECT c.name, sum(o.total) AS total_sum
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name
HAVING sum(o.total) > 200;
```

### Накопительная сумма

```sql
SELECT c.name,
       o.created_at,
       o.total,
       sum(o.total) OVER (
           PARTITION BY c.id
           ORDER BY o.created_at
       ) AS running_total
FROM customers c
JOIN orders o ON o.customer_id = c.id
ORDER BY c.name, o.created_at;
```

## Типовые ошибки

- `WHERE` нельзя использовать для фильтрации результата агрегата `sum(...)`; для этого нужен `HAVING`.
- `JOIN` без условия может создать лишние комбинации строк.
- В оконных функциях важно указывать `PARTITION BY` и `ORDER BY`, если расчёт зависит от группы и порядка.
- Для проверки перед `UPDATE` или `DELETE` сначала лучше написать `SELECT` с тем же `WHERE`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Короткий вывод

Практические задания должны дополнять official corpus и curated explanations. В tutorial-режиме лучше давать пользователю маленькую схему, набор данных, задания и проверочные решения.
