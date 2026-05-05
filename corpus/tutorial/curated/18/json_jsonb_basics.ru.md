---
title: "JSON и JSONB в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "json_jsonb_basics"
tags:
  - "json"
  - "jsonb"
  - "GIN"
  - "operators"
  - "data types"
official_backing:
  - "https://www.postgresql.org/docs/18/datatype-json.html"
  - "https://www.postgresql.org/docs/18/functions-json.html"
  - "https://www.postgresql.org/docs/18/indexes-types.html"
  - "https://www.postgresql.org/docs/18/gin.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# JSON и JSONB в PostgreSQL 18

## Назначение

Объяснить разницу между `json` и `jsonb`, базовые операции и когда использовать GIN-индекс.

Этот файл написан для режима `tutorial` и особенно для `extended_mode=true`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

`json` хранит текст JSON ближе к исходному виду. `jsonb` хранит разобранное бинарное представление, удобное для поиска, операторов и индексации. В прикладных системах чаще выбирают `jsonb`.

## Когда использовать

- что выбрать json или jsonb;
- как искать по JSON;
- GIN индекс для jsonb;
- как хранить гибкие атрибуты;

## Предварительные условия

- данные действительно имеют гибкую структуру;
- понятно, какие поля часто фильтруются;
- важные связи не спрятаны без необходимости внутри JSON;

## Пошаговая инструкция

### Шаг 1. Создать таблицу с jsonb

```sql
CREATE TABLE events (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamp DEFAULT now()
);
```

### Шаг 2. Добавить данные

```sql
INSERT INTO events (event_type, payload)
VALUES
('user_created', '{"user_id": 1, "email": "a@example.com", "active": true}'),
('user_created', '{"user_id": 2, "email": "b@example.com", "active": false}');
```

### Шаг 3. Получить поле как JSON и как текст

```sql
SELECT payload -> 'email' AS email_json,
       payload ->> 'email' AS email_text
FROM events;
```

### Шаг 4. Фильтровать по полю

```sql
SELECT * FROM events WHERE payload ->> 'email' = 'a@example.com';
```

### Шаг 5. Использовать containment

```sql
SELECT * FROM events WHERE payload @> '{"active": true}'::jsonb;
```

### Шаг 6. Создать GIN-индекс

```sql
CREATE INDEX events_payload_gin_idx ON events USING gin (payload);
```

## Проверка результата

- используется `jsonb`, если нужны поиск и индексация;
- важные поля модели не спрятаны в JSON без причины;
- индекс создан под реальные запросы;
- `EXPLAIN` подтверждает пользу индекса;

## Типовые ошибки и как думать

### Хранить всё в одном jsonb

если данные имеют строгую структуру и связи, лучше обычные колонки и foreign keys.

### Хранить числа как строки

это усложняет сравнения и сортировку.

### Ждать, что GIN ускорит любой запрос

индекс полезен только для подходящих операторов и условий.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

В PostgreSQL 18 для большинства практических задач выбирают `jsonb`, потому что он удобен для операторов, поиска и GIN-индексов. Важные поля и связи лучше хранить обычными колонками, а `jsonb` использовать для гибких дополнительных атрибутов.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `JSON Types`;
- `JSON Functions and Operators`;
- `GIN Indexes`;
- `Index Types`;
