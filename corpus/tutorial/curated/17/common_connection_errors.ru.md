---
title: "Типовые ошибки подключения и прав в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "common_connection_errors"
tags:
  - "errors"
  - "connection"
  - "authentication"
  - "roles"
  - "troubleshooting"
official_backing:
  - "https://www.postgresql.org/docs/17/client-authentication.html"
  - "https://www.postgresql.org/docs/17/auth-pg-hba-conf.html"
  - "https://www.postgresql.org/docs/17/user-manag.html"
  - "https://www.postgresql.org/docs/17/database-roles.html"
  - "https://www.postgresql.org/docs/17/app-psql.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Типовые ошибки подключения и прав в PostgreSQL 17

## Назначение

Дать понятный алгоритм диагностики частых ошибок подключения, аутентификации и прав доступа.

Этот файл написан для режима `tutorial` и особенно для `extended_mode=true`. Он не заменяет официальную документацию PostgreSQL 17, а помогает объяснять её проще и пошагово.

## Простое объяснение

Ошибка подключения может возникнуть на разных уровнях: клиентская утилита, сеть, `pg_hba.conf`, пароль, отсутствие роли/базы или нехватка прав на объект. Диагностика должна идти от простого к сложному.

## Когда использовать

- connection refused;
- role does not exist;
- database does not exist;
- password authentication failed;
- permission denied;

## Предварительные условия

- есть точный текст ошибки;
- известна команда подключения;
- есть доступ к серверу или администратору;

## Пошаговая инструкция

### Шаг 1. Проверить клиент

```bash
psql --version
```

### Шаг 2. Проверить адрес и порт

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres
```

### Шаг 3. Проверить текущего пользователя

```sql
SELECT current_user, current_database();
```

### Шаг 4. Посмотреть роли

```sql
SELECT rolname, rolcanlogin FROM pg_roles ORDER BY rolname;
```

### Шаг 5. Посмотреть базы

```sql
SELECT datname FROM pg_database ORDER BY datname;
```

### Шаг 6. Найти pg_hba.conf

```sql
SHOW hba_file;
```

### Шаг 7. Проверить права на таблицу

```sql
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public';
```

## Проверка результата

- точный текст ошибки сопоставлен с уровнем проблемы;
- роль существует и имеет `LOGIN`;
- база существует;
- есть правило в `pg_hba.conf`;
- права выданы на схему и таблицу;

## Типовые ошибки и как думать

### Исправлять всё сразу

лучше проверить уровни по порядку, иначе можно добавить небезопасные настройки.

### Путать пользователя ОС и роль PostgreSQL

это разные сущности, даже если имена совпадают.

### Выдавать слишком широкие права

для диагностики не нужно сразу выдавать `SUPERUSER`.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 17.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

При ошибках PostgreSQL сначала определи уровень: `psql`, сеть, `pg_hba.conf`, пароль, роль/база или права. Затем проверяй `current_user`, `pg_roles`, `pg_database`, `SHOW hba_file` и выдавай минимально необходимые права.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Client Authentication`;
- `pg_hba.conf`;
- `Database Roles`;
- `psql`;
- `GRANT`;
