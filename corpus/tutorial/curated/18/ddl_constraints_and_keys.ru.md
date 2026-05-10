---
title: "Таблицы, типы данных, ключи и ограничения в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "ddl_constraints_and_keys"
tags:
  - "DDL"
  - "constraints"
  - "primary key"
  - "foreign key"
  - "check"
official_backing:
  - "https://www.postgresql.org/docs/18/ddl.html"
  - "https://www.postgresql.org/docs/18/ddl-basics.html"
  - "https://www.postgresql.org/docs/18/ddl-constraints.html"
  - "https://www.postgresql.org/docs/18/datatype.html"
  - "https://www.postgresql.org/docs/18/sql-createtable.html"
external_reference:
  - "https://www.crunchydata.com/developers/tutorials"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Таблицы, типы данных, ключи и ограничения в PostgreSQL 18

## Назначение

Этот материал помогает строить таблицы так, чтобы корректность данных обеспечивалась самой базой: через типы, ключи и ограничения. Он закрывает частые вопросы начинающих: зачем нужны `PRIMARY KEY`/`FOREIGN KEY`, где применять `CHECK`, и почему проверок только в приложении недостаточно.

## Когда использовать

- проектируется новая схема данных;
- нужно добавить целостность в уже существующие таблицы;
- есть повторяющиеся ошибки качества данных;
- требуется формализовать связи между таблицами;
- нужно подготовить безопасную DDL-миграцию.

## Простое объяснение

Типы данных и ограничения в PostgreSQL — это "контракт" данных. Если контракт задан в DDL, база автоматически отклоняет некорректные записи. Это уменьшает зависимость от кода приложения и снижает риск появления "тихой" неконсистентности.

Базовый набор почти всегда включает: `PRIMARY KEY` для идентификации, `NOT NULL` для обязательных колонок, `UNIQUE` для уникальных бизнес-полей, `FOREIGN KEY` для ссылочной целостности и `CHECK` для доменных правил (например, сумма не может быть отрицательной).

## Предварительные условия

- есть модель предметной области и сущностей;
- выбран strategy для ключей (identity/UUID и т.д.);
- понятны правила удаления/обновления связанных данных;
- есть окно для миграции и проверки обратной совместимости;
- есть тесты, покрывающие ожидаемые отказные сценарии ограничений.

## Минимальный рабочий пример

```sql
CREATE TABLE app_users (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE,
    full_name text NOT NULL,
    age integer CHECK (age >= 0),
    created_at timestamp NOT NULL DEFAULT now()
);
```

```sql
CREATE TABLE orders (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES app_users(id) ON DELETE RESTRICT,
    total numeric(12,2) NOT NULL CHECK (total >= 0),
    status text NOT NULL DEFAULT 'new'
);
```

```sql
ALTER TABLE orders
ADD CONSTRAINT orders_status_check
CHECK (status IN ('new', 'paid', 'cancelled'));
```

## Пошаговый алгоритм

1. Определи обязательные поля и задай для них `NOT NULL`.
2. Выбери ключ таблицы и зафиксируй его как `PRIMARY KEY`.
3. Для естественных уникальных значений добавь `UNIQUE`.
4. Свяжи таблицы через `FOREIGN KEY` с явной политикой `ON DELETE/ON UPDATE`.
5. Добавь `CHECK` для доменных инвариантов.
6. Прогони тестовые вставки/обновления и убедись, что неверные данные блокируются.
7. Для существующих таблиц в production планируй миграции поэтапно, с предварительной очисткой грязных данных.

## Как проверить результат

```sql
SELECT conname, contype, conrelid::regclass AS table_name,
       pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid IN ('app_users'::regclass, 'orders'::regclass)
ORDER BY conrelid::regclass::text, conname;
```

```sql
INSERT INTO orders (user_id, total, status)
VALUES (999999, 100.00, 'new');
```

```sql
INSERT INTO orders (user_id, total, status)
VALUES (1, -10.00, 'new');
```

- `pg_constraint` должен отражать все ожидаемые ограничения;
- тестовые некорректные вставки должны завершаться ошибками ограничений;
- корректные записи должны успешно проходить.

## Типовые ошибки

- Хранить разные сущности как `text` без доменной структуры.
- Забывать `NOT NULL` и получать "пустые" обязательные поля.
- Не задавать `FOREIGN KEY`, а проверять связи только в коде приложения.
- Использовать слишком мягкие `CHECK`, которые не отражают бизнес-правила.
- Добавлять ограничения в production без предварительной проверки существующих данных.

## Безопасность и ограничения

- Ограничения повышают качество данных, но могут ломать старые интеграции с грязным входом.
- Непродуманная FK-политика может неожиданно блокировать удаление/обновление.
- DDL-изменения в production нужно выполнять через контролируемые миграции.
- Этот материал обучающий: нюансы каждого типа/ограничения уточняй в official docs версии 18.

## Что искать в official corpus

- `https://www.postgresql.org/docs/18/ddl.html`
- `https://www.postgresql.org/docs/18/ddl-basics.html`
- `https://www.postgresql.org/docs/18/ddl-constraints.html`
- `https://www.postgresql.org/docs/18/datatype.html`
- `https://www.postgresql.org/docs/18/sql-createtable.html`

## Короткий вывод

Качественная DDL-модель в PostgreSQL строится на типах и ограничениях, а не только на логике приложения. `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE` и `CHECK` вместе дают устойчивый уровень целостности данных. Чем раньше эти правила встроены в схему, тем меньше технического долга и скрытых ошибок в будущем.
