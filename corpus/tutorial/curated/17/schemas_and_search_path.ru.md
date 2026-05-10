---
title: "Схемы и search_path в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "schemas_and_search_path"
tags:
  - "schema"
  - "search_path"
  - "namespace"
  - "permissions"
official_backing:
  - "https://www.postgresql.org/docs/17/ddl-schemas.html"
  - "https://www.postgresql.org/docs/17/runtime-config-client.html"
  - "https://www.postgresql.org/docs/17/sql-createschema.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Схемы и search_path в PostgreSQL 17

## Назначение

Этот материал объясняет, как правильно организовать схемы и управлять `search_path`, чтобы объекты находились предсказуемо и безопасно. Он нужен, когда возникают ошибки вида "relation does not exist" при наличии таблицы, а также когда требуется разделение объектов по ролям и окружениям.

## Когда использовать

- приложение использует несколько схем внутри одной базы;
- нужно изолировать объекты разных модулей/команд;
- есть риск путаницы из-за неявного поиска объектов;
- требуется навести порядок в правах на schema и table;
- нужно уменьшить зависимость от `public` по умолчанию.

## Простое объяснение

Схема в PostgreSQL — это namespace внутри базы. Если в SQL написать имя без префикса схемы, PostgreSQL ищет объект по списку `search_path` слева направо. Поэтому одна и та же команда может работать по-разному для разных ролей, если у них разный `search_path`.

Практический принцип: для приложения лучше иметь выделенную схему (например, `app`) и явно задавать `search_path` для прикладной роли. Это уменьшает случайные коллизии имён и делает поведение SQL более предсказуемым.

## Предварительные условия

- определена схема именования и границы модулей;
- есть прикладная роль (`app_user`) и административная роль;
- согласованы права `USAGE`/`CREATE` на схемы;
- есть понимание, какие объекты должны оставаться в `public`, а какие нет;
- миграции умеют явно указывать схему.

## Минимальный рабочий пример

```sql
SHOW search_path;
SELECT current_schemas(true);
```

```sql
CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.orders (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    total numeric(10,2) NOT NULL
);
```

```sql
GRANT USAGE ON SCHEMA app TO app_user;
GRANT CREATE ON SCHEMA app TO app_user;
```

```sql
ALTER ROLE app_user SET search_path = app, public;
```

## Пошаговый алгоритм

1. Зафиксируй целевую схему объектов приложения (например, `app`).
2. Создай схему и перенеси/создай в ней нужные таблицы, функции и индексы.
3. Настрой права на схему: `USAGE` для доступа, `CREATE` только где это нужно.
4. Установи `search_path` для роли приложения через `ALTER ROLE`.
5. В миграциях и критичных SQL используй schema-qualified имена (`app.orders`).
6. Проверь поведение под прикладной ролью и админской ролью отдельно.
7. Зафиксируй стандарт: где допускаются объекты в `public`, а где нет.

## Как проверить результат

```sql
SHOW search_path;
SELECT current_schemas(true);
```

```sql
SELECT n.nspname AS schema_name, c.relname AS table_name
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND c.relname = 'orders';
```

```sql
SELECT has_schema_privilege('app_user', 'app', 'USAGE') AS has_usage,
       has_schema_privilege('app_user', 'app', 'CREATE') AS has_create;
```

- таблицы создаются и находятся в ожидаемой схеме;
- `search_path` у прикладной роли соответствует политике проекта;
- роль имеет ровно нужные права на схему, без избыточных grant.

## Типовые ошибки

- Полагаться на `public` и не контролировать namespace объектов.
- Выдать права на таблицы, но забыть `USAGE` на схему.
- Не задавать `search_path` для прикладной роли и получать нестабильное поведение.
- Писать миграции без схемы и получать объекты "не там".
- Использовать одинаковые имена таблиц в разных схемах без осознанной необходимости.

## Безопасность и ограничения

- Неаккуратный `search_path` может привести к непредсказуемому разрешению объектов.
- В production доступ на `CREATE` в рабочих схемах должен быть минимальным.
- Множественные схемы повышают гибкость, но требуют дисциплины в миграциях и ревью.
- Учебный материал не заменяет policy доступа и security-review на уровне организации.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/ddl-schemas.html`
- `https://www.postgresql.org/docs/17/runtime-config-client.html`
- `https://www.postgresql.org/docs/17/sql-createschema.html`

## Короткий вывод

Схемы и `search_path` в PostgreSQL определяют, где живут объекты и как SQL находит их без явного префикса. Для приложений лучше закреплять отдельную схему и явные правила прав/миграций. Это снижает ошибки "объект не найден" и делает поведение среды стабильным.
