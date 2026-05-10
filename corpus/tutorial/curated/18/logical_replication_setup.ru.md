---
title: "Пошаговая настройка logical replication в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "logical_replication_setup"
tags:
  - "logical replication"
  - "publication"
  - "subscription"
  - "wal_level"
  - "replication"
official_backing:
  - "https://www.postgresql.org/docs/18/logical-replication.html"
  - "https://www.postgresql.org/docs/18/logical-replication-publication.html"
  - "https://www.postgresql.org/docs/18/logical-replication-subscription.html"
  - "https://www.postgresql.org/docs/18/logical-replication-config.html"
  - "https://www.postgresql.org/docs/18/runtime-config-replication.html"
  - "https://www.postgresql.org/docs/18/sql-createpublication.html"
  - "https://www.postgresql.org/docs/18/sql-createsubscription.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Пошаговая настройка logical replication в PostgreSQL 18

## Назначение

Дать понятную пошаговую инструкцию по настройке logical replication между publisher и subscriber.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

Logical replication работает по модели publish/subscribe. На источнике создают `publication`, на получателе — `subscription`. Publisher отправляет изменения выбранных таблиц, subscriber принимает и применяет их.

## Когда использовать

- как настроить logical replication;
- publication subscription;
- wal_level logical;
- репликация между версиями;
- репликация выбранных таблиц;

## Предварительные условия

- два сервера или две базы PostgreSQL;
- сетевой доступ от subscriber к publisher;
- таблицы желательно имеют primary key;
- роль для репликации имеет нужные права;
- `wal_level` на publisher настроен как `logical`;

## Пошаговая инструкция

### Шаг 1. Проверить параметры на publisher

```sql
SHOW wal_level;
SHOW max_replication_slots;
SHOW max_wal_senders;
```

### Шаг 2. Создать роль для репликации

```sql
CREATE ROLE repl_user WITH LOGIN REPLICATION PASSWORD 'strong_password';
```

### Шаг 3. Выдать права чтения для начальной копии

```sql
GRANT CONNECT ON DATABASE source_db TO repl_user;
GRANT USAGE ON SCHEMA public TO repl_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repl_user;
```

### Шаг 4. Разрешить доступ в pg_hba.conf

```text
host    source_db    repl_user    192.168.1.20/32    scram-sha-256
```

### Шаг 5. Создать таблицу на publisher

```sql
CREATE TABLE public.products (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    price numeric(10,2) NOT NULL
);
```

### Шаг 6. Создать совместимую таблицу на subscriber

```sql
CREATE TABLE public.products (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    price numeric(10,2) NOT NULL
);
```

### Шаг 7. Создать publication

```sql
CREATE PUBLICATION products_pub FOR TABLE public.products;
```

### Шаг 8. Создать subscription

```sql
CREATE SUBSCRIPTION products_sub
CONNECTION 'host=192.168.1.10 port=5432 dbname=source_db user=repl_user password=strong_password'
PUBLICATION products_pub;
```

### Шаг 9. Проверить передачу данных

```sql
-- publisher
INSERT INTO public.products (name, price) VALUES ('monitor', 300.00);

-- subscriber
SELECT * FROM public.products ORDER BY id;
```

## Проверка результата

- `pg_subscription` на subscriber содержит subscription;
- `pg_publication` на publisher содержит publication;
- тестовая строка появляется на subscriber;
- в логах нет ошибок применения изменений;

## Типовые ошибки и как думать

### `wal_level` не равен `logical`

logical replication не сможет корректно работать.

### У роли нет `REPLICATION`

replication connection требует соответствующих прав или superuser.

### Нет SELECT на таблицах

начальная синхронизация не сможет прочитать данные.

### Таблица на subscriber не совместима

применение изменений может завершиться ошибкой.

### Писать в реплицируемую таблицу на subscriber

можно получить конфликты данных.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для logical replication в PostgreSQL 18 на publisher включают `wal_level=logical`, проверяют `max_replication_slots` и `max_wal_senders`, создают роль с `REPLICATION`, настраивают `pg_hba.conf`, создают `CREATE PUBLICATION`, а на subscriber — совместимую таблицу и `CREATE SUBSCRIPTION`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Logical Replication`;
- `Publication`;
- `Subscription`;
- `Runtime Configuration / Replication`;
- `CREATE PUBLICATION`;
- `CREATE SUBSCRIPTION`;
