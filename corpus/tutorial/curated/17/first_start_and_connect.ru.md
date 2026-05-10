---
title: "Первый запуск PostgreSQL 17 и подключение через psql"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "first_start_and_connect"
tags:
  - "psql"
  - "connection"
  - "createdb"
  - "beginner"
  - "tutorial"
official_backing:
  - "https://www.postgresql.org/docs/17/tutorial.html"
  - "https://www.postgresql.org/docs/17/tutorial-start.html"
  - "https://www.postgresql.org/docs/17/tutorial-createdb.html"
  - "https://www.postgresql.org/docs/17/tutorial-accessdb.html"
  - "https://www.postgresql.org/docs/17/app-psql.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Первый запуск PostgreSQL 17 и подключение через psql

## Назначение

Объяснить новичку, как проверить доступность PostgreSQL, подключиться через `psql`, создать учебную базу и выполнить первые SQL-команды.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 17, а помогает объяснять её проще и пошагово.

## Простое объяснение

PostgreSQL работает как сервер. `psql` — это клиентская программа: она подключается к серверу, выбирает базу данных и отправляет SQL-команды. Для успешного старта нужны запущенный сервер, существующая роль с правом входа и база данных, к которой можно подключиться.

## Когда использовать

- как начать работу с PostgreSQL;
- как открыть psql;
- как создать первую базу;
- почему не получается подключиться;
- как проверить версию сервера;

## Предварительные условия

- PostgreSQL установлен локально, в Docker или на сервере;
- известна выбранная major-версия;
- есть доступ к терминалу;
- известны имя роли и база данных либо есть административный доступ;

## Пошаговая инструкция

### Шаг 1. Проверить клиентскую утилиту

```bash
psql --version
```

### Шаг 2. Подключиться к стандартной базе

```bash
psql -U postgres -d postgres
```

### Шаг 3. Если сервер не локальный, указать host и port

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres
```

### Шаг 4. Проверить контекст подключения

```sql
SELECT version();
SELECT current_database();
SELECT current_user;
```

### Шаг 5. Посмотреть список баз

```text
\l
```

### Шаг 6. Создать учебную базу

```sql
CREATE DATABASE demo_db;
```

### Шаг 7. Переключиться на неё

```text
\c demo_db
```

### Шаг 8. Создать тестовую таблицу

```sql
CREATE TABLE notes (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title text NOT NULL,
    created_at timestamp DEFAULT now()
);
```

### Шаг 9. Добавить и прочитать строку

```sql
INSERT INTO notes (title) VALUES ('Первая запись');
SELECT * FROM notes;
```

## Проверка результата

- `SELECT current_database(), current_user;` возвращает ожидаемую базу и роль;
- `\dt` показывает созданную таблицу;
- `SELECT * FROM notes;` возвращает тестовую запись;

## Типовые ошибки и как думать

### `psql: command not found`

клиентская утилита не установлена или не находится в `PATH`. Нужно установить PostgreSQL client tools или запускать команду в окружении контейнера.

### `connection refused`

сервер не принимает TCP-соединение: он не запущен, выбран неверный порт, не проброшен Docker-порт или сервер слушает другой адрес.

### `role does not exist`

указанной роли нет в кластере PostgreSQL. Нужно подключиться существующей ролью или создать роль с `LOGIN`.

### `database does not exist`

указанной базы нет. Нужно создать базу через `CREATE DATABASE` или подключиться к существующей базе, например `postgres`.

### `password authentication failed`

роль существует, но пароль неверный или метод аутентификации в `pg_hba.conf` требует другой способ входа.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 17.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Чтобы начать работу с PostgreSQL 17, проверь `psql --version`, подключись через `psql -U <role> -d <database>`, проверь `SELECT version()`, создай учебную базу через `CREATE DATABASE`, затем создай таблицу и выполни `INSERT`/`SELECT`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Tutorial / Getting Started`;
- `Creating a Database`;
- `Accessing a Database`;
- `psql`;
- `CREATE DATABASE`;
