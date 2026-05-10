---
title: "Роли, пользователи и базы данных в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "roles_users_and_databases"
tags:
  - "roles"
  - "users"
  - "permissions"
  - "createdb"
  - "grant"
official_backing:
  - "https://www.postgresql.org/docs/18/user-manag.html"
  - "https://www.postgresql.org/docs/18/database-roles.html"
  - "https://www.postgresql.org/docs/18/role-attributes.html"
  - "https://www.postgresql.org/docs/18/sql-createrole.html"
  - "https://www.postgresql.org/docs/18/sql-createdatabase.html"
  - "https://www.postgresql.org/docs/18/sql-grant.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Роли, пользователи и базы данных в PostgreSQL 18

## Назначение

Пояснить, как в PostgreSQL связаны роли, пользователи, базы данных и права доступа.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

В PostgreSQL основной объект безопасности — `role`. Роль может быть пользователем, если у неё есть `LOGIN`, или группой, если ей выдают права и включают в неё другие роли. Базы данных живут внутри кластера, а роли действуют на уровне всего кластера.

## Когда использовать

- как создать пользователя;
- почему role does not exist;
- как выдать права;
- что такое LOGIN;
- почему permission denied;

## Предварительные условия

- есть административная роль или роль с нужными правами;
- понятно, для какой базы выдаются права;
- известна схема и таблицы, к которым нужен доступ;

## Пошаговая инструкция

### Шаг 1. Подключиться администратором

```bash
psql -U postgres -d postgres
```

### Шаг 2. Создать роль-пользователя

```sql
CREATE ROLE app_user WITH LOGIN PASSWORD 'strong_password';
```

### Шаг 3. Создать базу с владельцем

```sql
CREATE DATABASE app_db OWNER app_user;
```

### Шаг 4. Подключиться под новой ролью

```bash
psql -U app_user -d app_db
```

### Шаг 5. Проверить текущий контекст

```sql
SELECT current_user, current_database();
```

### Шаг 6. Выдать право подключения к существующей базе

```sql
GRANT CONNECT ON DATABASE app_db TO app_user;
```

### Шаг 7. Выдать право использовать схему

```sql
GRANT USAGE ON SCHEMA public TO app_user;
```

### Шаг 8. Выдать права на таблицу

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.items TO app_user;
```

### Шаг 9. Создать роль-группу для чтения

```sql
CREATE ROLE readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT readonly TO app_user;
```

## Проверка результата

- `\du` показывает роль и её атрибуты;
- `SELECT rolname, rolcanlogin FROM pg_roles;` показывает, может ли роль входить;
- `current_user` совпадает с ожидаемой ролью;

## Типовые ошибки и как думать

### Создать роль без `LOGIN`

такая роль удобна как группа, но под ней нельзя подключиться как пользователь.

### Выдать только права на таблицу, но забыть `USAGE` на схему

пользователь может получить `permission denied for schema`.

### Всем выдавать `SUPERUSER`

это опасно. Для приложения обычно нужна отдельная роль с минимальными правами.

### Считать роли локальными для базы

роли существуют на уровне кластера, а не отдельной базы.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

В PostgreSQL пользователь — это роль с `LOGIN`. Для приложения обычно создают отдельную роль, базу с `OWNER`, затем выдают минимальные права через `GRANT`; `SUPERUSER` не нужен для обычной работы приложения.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Database Roles`;
- `Role Attributes`;
- `CREATE ROLE`;
- `CREATE DATABASE`;
- `GRANT`;
- `Privileges`;
