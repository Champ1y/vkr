---
title: "Удалённый доступ, listen_addresses и pg_hba.conf в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "remote_access_pg_hba"
tags:
  - "pg_hba.conf"
  - "listen_addresses"
  - "authentication"
  - "remote access"
official_backing:
  - "https://www.postgresql.org/docs/18/client-authentication.html"
  - "https://www.postgresql.org/docs/18/auth-pg-hba-conf.html"
  - "https://www.postgresql.org/docs/18/runtime-config-connection.html"
  - "https://www.postgresql.org/docs/18/auth-password.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Удалённый доступ, listen_addresses и pg_hba.conf в PostgreSQL 18

## Назначение

Объяснить, как PostgreSQL разрешает или запрещает подключения с других машин.

Этот файл написан для режима `tutorial` и особенно для `extended_mode=true`. Он не заменяет официальную документацию PostgreSQL 18, а помогает объяснять её проще и пошагово.

## Простое объяснение

Для удалённого подключения должны совпасть три уровня: сервер слушает нужный адрес через `listen_addresses`, порт доступен по сети, а `pg_hba.conf` содержит правило для нужной базы, роли и IP-адреса.

## Когда использовать

- как открыть доступ с другого компьютера;
- no pg_hba.conf entry;
- connection refused;
- как настроить пароль;
- как разрешить доступ в локальной сети;

## Предварительные условия

- известен IP клиента;
- известны база и роль;
- есть доступ к конфигурационным файлам или SQL-командам `SHOW`;
- понятно, локальный это сервер или Docker;

## Пошаговая инструкция

### Шаг 1. Найти конфигурационные файлы

```sql
SHOW config_file;
SHOW hba_file;
```

### Шаг 2. Проверить адрес и порт

```sql
SHOW listen_addresses;
SHOW port;
```

### Шаг 3. Настроить адрес прослушивания

```text
listen_addresses = '192.168.1.10'
```

### Шаг 4. Добавить точное правило в pg_hba.conf

```text
host    app_db    app_user    192.168.1.0/24    scram-sha-256
```

### Шаг 5. Перечитать pg_hba.conf

```sql
SELECT pg_reload_conf();
```

### Шаг 6. Проверить подключение с клиента

```bash
psql -h 192.168.1.10 -p 5432 -U app_user -d app_db
```

## Проверка результата

- `SHOW hba_file;` показывает редактируемый файл;
- после `pg_reload_conf()` ошибка `no pg_hba.conf entry` исчезает;
- подключение с указанного IP проходит только для нужной роли/базы;

## Типовые ошибки и как думать

### Использовать `host all all 0.0.0.0/0 trust`

это слишком широкое и небезопасное правило.

### Поменять `pg_hba.conf`, но не выполнить reload

сервер продолжит использовать старые правила.

### Поменять `listen_addresses`, но не перезапустить сервер

для некоторых параметров нужен restart.

### Открыть firewall, но забыть `pg_hba.conf`

сетевой доступ не заменяет правило аутентификации.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 18.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для удалённого доступа в PostgreSQL 18 проверь `listen_addresses`, доступность порта, добавь точное правило в `pg_hba.conf`, выполни `SELECT pg_reload_conf()` и подключись через `psql -h <host> -U <role> -d <database>`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 18. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Client Authentication`;
- `The pg_hba.conf File`;
- `Connection Settings`;
- `Password Authentication`;
