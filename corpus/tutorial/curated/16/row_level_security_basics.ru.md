---
title: "Основы Row Level Security в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "row_level_security_basics"
tags:
  - "RLS"
  - "row level security"
  - "policy"
  - "security"
official_backing:
  - "https://www.postgresql.org/docs/16/ddl-rowsecurity.html"
  - "https://www.postgresql.org/docs/16/sql-createpolicy.html"
  - "https://www.postgresql.org/docs/16/sql-altertable.html"
external_reference:
  - "https://www.crunchydata.com/developers/tutorials"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Основы Row Level Security в PostgreSQL 16

## Назначение

Этот материал объясняет, как включить и проверить Row Level Security (RLS), чтобы ограничивать доступ к строкам на уровне политики. Он особенно полезен для multi-tenant систем, где важно, чтобы один пользователь или tenant не видел чужие данные.

## Когда использовать

- в одной таблице хранятся данные нескольких tenants;
- нужен централизованный контроль доступа на уровне базы, а не только приложения;
- необходимо ограничить `SELECT` и `INSERT/UPDATE/DELETE` разными правилами;
- требуется снизить риск утечки данных из-за ошибок в SQL приложения;
- нужно формализовать и тестировать политику доступа.

## Простое объяснение

RLS добавляет к запросам невидимый фильтр: какие строки роль может читать и какие может изменять. Политики задаются через `CREATE POLICY`, а на таблице включаются через `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.

Обычно есть две отдельные части политики: `USING` для чтения/видимости строк и `WITH CHECK` для контроля того, какие строки можно вставлять или обновлять. Это помогает не только скрыть чужие строки, но и запретить пользователю записать "чужой tenant_id".

Важно помнить: RLS — сильный инструмент, но его нужно тестировать под разными ролями и режимами доступа. Неверно построенная policy может либо закрыть легитимный доступ, либо оставить обходные пути.

## Предварительные условия

- есть чёткая модель субъектов доступа (tenant, user, service role);
- таблицы содержат колонку для изоляции (например, `tenant_id`);
- роли и права на таблицы настроены базово (GRANT/REVOKE);
- есть безопасный способ передавать tenant-контекст в сессию;
- есть набор тест-кейсов на чтение и запись с разными ролями.

## Минимальный рабочий пример

```sql
CREATE TABLE tenant_documents (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id integer NOT NULL,
    title text NOT NULL,
    body text NOT NULL
);
```

```sql
ALTER TABLE tenant_documents ENABLE ROW LEVEL SECURITY;
```

```sql
CREATE POLICY tenant_documents_select_policy
ON tenant_documents
FOR SELECT
USING (tenant_id = current_setting('app.tenant_id')::integer);
```

```sql
CREATE POLICY tenant_documents_write_policy
ON tenant_documents
FOR INSERT, UPDATE
WITH CHECK (tenant_id = current_setting('app.tenant_id')::integer);
```

```sql
SET app.tenant_id = '1';
SELECT id, tenant_id, title FROM tenant_documents ORDER BY id;
```

## Пошаговый алгоритм

1. Определи колонку изоляции (например, `tenant_id`) и правила доступа для операций чтения/записи.
2. Включи RLS на таблице через `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.
3. Создай политику `USING` для `SELECT`.
4. Добавь `WITH CHECK` для `INSERT/UPDATE`, чтобы запретить подмену tenant.
5. Проверь выдачу прав на таблицу и схему для прикладных ролей.
6. Протестируй поведение под несколькими tenant-контекстами и ролями.
7. Зафиксируй policy в миграции и добавь regression-тесты на безопасность.

## Как проверить результат

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'tenant_documents';
```

```sql
SET app.tenant_id = '1';
SELECT count(*) FROM tenant_documents;

SET app.tenant_id = '2';
SELECT count(*) FROM tenant_documents;
```

```sql
SET app.tenant_id = '1';
INSERT INTO tenant_documents (tenant_id, title, body)
VALUES (2, 'bad write', 'should fail');
```

- под разными tenant-контекстами видимость строк меняется ожидаемо;
- попытка вставить/обновить строку с чужим `tenant_id` блокируется policy;
- `pg_policies` отражает нужные правила для SELECT и write-операций.

## Типовые ошибки

- Создать policy, но забыть включить RLS на таблице.
- Проверить только чтение и не проверить `WITH CHECK` для записи.
- Давать приложению роль с чрезмерными правами и обходом intended-политики.
- Передавать tenant-контекст ненадёжно, без валидации источника.
- Не покрыть RLS тестами в CI и получить регрессии после миграций.

## Безопасность и ограничения

- RLS не заменяет архитектурную безопасность: нужны корректные роли, grants и аудит.
- Политики могут усложнять запросы и диагностику, особенно при множестве ролей.
- Ошибка в policy потенциально критична: либо утечка, либо блокировка легитимного доступа.
- Для production нужны security-тесты и review policy-изменений как обязательный этап.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 16. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/16/ddl-rowsecurity.html`
- `https://www.postgresql.org/docs/16/sql-createpolicy.html`
- `https://www.postgresql.org/docs/16/sql-altertable.html`

## Короткий вывод

RLS позволяет enforce-ить изоляцию данных на стороне PostgreSQL и снижать риск ошибок в прикладном SQL. Базовая схема: включить RLS, задать `USING` для чтения и `WITH CHECK` для записи, затем проверить под разными ролями и tenant-контекстами. Надёжность RLS определяется качеством тестов и дисциплиной управления правами.
