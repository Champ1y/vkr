---
title: "CTE, подзапросы и views в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "cte_subqueries_views"
tags:
  - "CTE"
  - "WITH"
  - "subquery"
  - "view"
  - "materialized view"
official_backing:
  - "https://www.postgresql.org/docs/18/queries-with.html"
  - "https://www.postgresql.org/docs/18/sql-createview.html"
  - "https://www.postgresql.org/docs/18/rules-materializedviews.html"
  - "https://www.postgresql.org/docs/18/sql-creatematerializedview.html"
external_reference:
  - "https://www.crunchydata.com/developers/tutorials"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# CTE, подзапросы и views в PostgreSQL 18

## Назначение

Этот материал объясняет, как выбирать между subquery, CTE (`WITH`), `CREATE VIEW` и `CREATE MATERIALIZED VIEW` в реальных задачах. Он нужен, когда запросы растут по сложности и команде важно сохранить читаемость, производительность и предсказуемое обновление данных.

## Когда использовать

- один SQL-запрос стал слишком сложным и плохо читается;
- нужно повторно использовать одну и ту же SQL-логику в нескольких местах;
- требуется ускорить тяжёлую агрегацию за счёт заранее сохранённого результата;
- нужно отделить слой представления данных от базовых таблиц;
- требуется объяснить, почему materialized view "устарела".

## Простое объяснение

Subquery — это вложенный запрос внутри другого запроса. Он удобен для локальной логики и часто хорошо оптимизируется planner-ом. CTE (`WITH`) помогает дать имя промежуточному набору строк и сделать запрос читабельнее, особенно если промежуточный результат используется несколько раз.

`VIEW` — это именованный SQL-запрос, который выполняется при каждом обращении. Он не хранит данные физически, а хранит определение запроса. `MATERIALIZED VIEW` хранит результат физически, поэтому может читать быстрее на тяжёлых отчётах, но не обновляется автоматически и требует `REFRESH MATERIALIZED VIEW`.

Ключевая идея выбора:
- subquery: простая локальная вложенность;
- CTE: сложный запрос, который нужно структурировать;
- VIEW: повторно используемая логика "всегда актуально, но считается на лету";
- MATERIALIZED VIEW: тяжёлая агрегация, которую приемлемо обновлять по расписанию.

## Предварительные условия

- есть базовые таблицы и понятные бизнес-правила агрегации;
- известна частота обновления данных и требования к актуальности;
- у роли есть права на `CREATE VIEW`/`CREATE MATERIALIZED VIEW`;
- есть план, как и когда выполнять `REFRESH MATERIALIZED VIEW`;
- есть понимание, кто будет читать объекты и какие grants нужны.

## Минимальный рабочий пример

```sql
WITH customer_totals AS (
    SELECT customer_id, sum(total) AS total_sum
    FROM orders
    GROUP BY customer_id
)
SELECT customer_id, total_sum
FROM customer_totals
WHERE total_sum > 1000;
```

```sql
CREATE VIEW active_customers AS
SELECT id, email
FROM customers
WHERE active = true;
```

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT date_trunc('month', created_at) AS month,
       sum(total) AS total_sum
FROM orders
GROUP BY 1;

REFRESH MATERIALIZED VIEW monthly_sales;
```

## Пошаговый алгоритм

1. Начни с простого subquery, если задача локальная и короткая.
2. Если запрос плохо читается, вынеси смысловые блоки в `WITH`-CTE.
3. Когда логика нужна в разных местах, оформи её как `CREATE VIEW`.
4. Если расчёт тяжёлый и допустима задержка актуальности, рассмотри `CREATE MATERIALIZED VIEW`.
5. Для materialized view сразу зафиксируй политику обновления (`REFRESH MATERIALIZED VIEW`).
6. Проверь права доступа к view/materialized view для прикладных ролей.
7. Сравни итоговые `SELECT` и планы выполнения, чтобы убедиться, что решение подходит под нагрузку.

## Как проверить результат

```text
\d active_customers
\d monthly_sales
```

```sql
SELECT * FROM active_customers LIMIT 10;
SELECT * FROM monthly_sales ORDER BY month DESC LIMIT 12;
```

```sql
REFRESH MATERIALIZED VIEW monthly_sales;
SELECT * FROM monthly_sales ORDER BY month DESC LIMIT 12;
```

- `\d` должен показывать созданные объекты и их тип;
- `SELECT` из view должен давать актуальные строки базовых таблиц;
- после `REFRESH MATERIALIZED VIEW` материализованный результат должен обновиться.

## Типовые ошибки

- Считать, что materialized view обновляется автоматически.
- Использовать CTE везде по привычке, даже когда subquery проще.
- Создать view и забыть выдать права ролям, которые её читают.
- Ожидать, что materialized view всегда подходит для OLTP-сценариев с высокой частотой изменений.
- Не документировать расписание refresh и получать "тихое устаревание" отчётов.

## Безопасность и ограничения

- View и materialized view могут раскрывать данные шире, чем планировалось, если grants настроены неаккуратно.
- Materialized view хранит физические данные, значит их нужно учитывать в storage и backup-стратегии.
- Частый refresh тяжёлой materialized view может заметно нагружать систему.
- Этот файл объясняет подход, но фактические ограничения синтаксиса и прав проверяй в official docs.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/18/queries-with.html`
- `https://www.postgresql.org/docs/18/sql-createview.html`
- `https://www.postgresql.org/docs/18/rules-materializedviews.html`
- `https://www.postgresql.org/docs/18/sql-creatematerializedview.html`

## Короткий вывод

Subquery, CTE, `VIEW` и `MATERIALIZED VIEW` решают похожие, но не одинаковые задачи. Для читаемости и поддержки часто достаточно `WITH` или `VIEW`, а для тяжёлых отчётов полезен `MATERIALIZED VIEW` с осознанным `REFRESH`. Главный критерий выбора — баланс между читаемостью, актуальностью данных и ценой вычисления.
