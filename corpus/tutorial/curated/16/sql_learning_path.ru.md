---
title: "Учебный маршрут по SQL в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "sql_learning_path"
tags:
  - "SQL"
  - "SELECT"
  - "JOIN"
  - "GROUP BY"
  - "transactions"
official_backing:
  - "https://www.postgresql.org/docs/16/tutorial-sql.html"
  - "https://www.postgresql.org/docs/16/tutorial-table.html"
  - "https://www.postgresql.org/docs/16/tutorial-select.html"
  - "https://www.postgresql.org/docs/16/tutorial-join.html"
  - "https://www.postgresql.org/docs/16/tutorial-agg.html"
  - "https://www.postgresql.org/docs/16/tutorial-transactions.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Учебный маршрут по SQL в PostgreSQL 16

## Назначение

Дать новичку последовательный путь изучения SQL на маленьком связанном примере.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 16, а помогает объяснять её проще и пошагово.

## Простое объяснение

SQL лучше изучать не как список отдельных команд, а как сценарий: создать таблицы, добавить данные, выбрать строки, соединить таблицы, посчитать агрегаты и попробовать транзакцию.

## Когда использовать

- объясни SQL;
- как изучать SELECT;
- JOIN;
- GROUP BY;
- транзакции;
- практика для новичка;

## Предварительные условия

- есть учебная база;
- пользователь может создавать таблицы;
- есть подключение через psql или другой клиент;

## Пошаговая инструкция

### Шаг 1. Создать таблицы

```sql
CREATE TABLE customers (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE orders (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES customers(id),
    total numeric(10,2) NOT NULL,
    created_at timestamp DEFAULT now()
);
```

### Шаг 2. Добавить данные

```sql
INSERT INTO customers (name) VALUES ('Alice'), ('Bob');
INSERT INTO orders (customer_id, total) VALUES (1, 100.00), (1, 50.00), (2, 200.00);
```

### Шаг 3. Выполнить SELECT

```sql
SELECT id, name FROM customers;
```

### Шаг 4. Добавить WHERE и ORDER BY

```sql
SELECT * FROM orders WHERE total > 100 ORDER BY total DESC;
```

### Шаг 5. Сделать JOIN

```sql
SELECT c.name, o.total
FROM customers c
JOIN orders o ON o.customer_id = c.id;
```

### Шаг 6. Сделать GROUP BY

```sql
SELECT c.name, sum(o.total) AS total_sum
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;
```

### Шаг 7. Попробовать транзакцию

```sql
BEGIN;
UPDATE orders SET total = total + 10 WHERE id = 1;
SELECT * FROM orders WHERE id = 1;
ROLLBACK;
```

## Проверка результата

- JOIN возвращает имена клиентов и заказы;
- GROUP BY считает сумму по клиентам;
- ROLLBACK отменяет учебное изменение;

## Типовые ошибки и как думать

### Забыть WHERE в UPDATE или DELETE

можно изменить или удалить все строки.

### Путать WHERE и HAVING

`WHERE` фильтрует строки до группировки, `HAVING` — группы после агрегирования.

### Делать JOIN без условия

получится нежелательная комбинация строк.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 16.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для изучения SQL в PostgreSQL 16 начни с `CREATE TABLE`, затем `INSERT`, `SELECT`, `WHERE`, `ORDER BY`, `JOIN`, `GROUP BY`, `HAVING`, `UPDATE`, `DELETE` и транзакций `BEGIN`/`COMMIT`/`ROLLBACK`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 16. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `The SQL Language`;
- `Creating a New Table`;
- `Querying a Table`;
- `Joins Between Tables`;
- `Aggregate Functions`;
- `Transactions`;
