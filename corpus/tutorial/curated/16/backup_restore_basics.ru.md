---
title: "Резервное копирование и восстановление в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "backup_restore_basics"
tags:
  - "backup"
  - "restore"
  - "pg_dump"
  - "pg_restore"
  - "psql"
  - "PITR"
official_backing:
  - "https://www.postgresql.org/docs/16/backup.html"
  - "https://www.postgresql.org/docs/16/backup-dump.html"
  - "https://www.postgresql.org/docs/16/app-pgdump.html"
  - "https://www.postgresql.org/docs/16/app-pgrestore.html"
  - "https://www.postgresql.org/docs/16/app-psql.html"
  - "https://www.postgresql.org/docs/16/continuous-archiving.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Резервное копирование и восстановление в PostgreSQL 16

## Назначение

Объяснить базовые способы backup/restore: SQL dump, custom archive, pg_restore и отличие от PITR.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 16, а помогает объяснять её проще и пошагово.

## Простое объяснение

`pg_dump` делает логическую копию одной базы данных. Plain SQL dump восстанавливается через `psql`, а custom-format dump — через `pg_restore`. Для всего кластера и ролей нужен другой подход, например `pg_dumpall`; для восстановления на точку времени используют WAL/PITR.

## Когда использовать

- как сделать backup;
- как восстановить базу;
- pg_dump;
- pg_restore;
- перенос базы;
- резервная копия перед экспериментом;

## Предварительные условия

- есть доступ к базе;
- достаточно места для dump;
- известно, нужна одна база или весь кластер;
- для восстановления подготовлена пустая база;

## Пошаговая инструкция

### Шаг 1. Создать plain SQL dump

```bash
pg_dump -U app_user -d app_db > app_db.sql
```

### Шаг 2. Создать пустую базу для восстановления

```bash
createdb -U postgres restored_db
```

### Шаг 3. Восстановить plain dump

```bash
psql -U postgres -d restored_db -f app_db.sql
```

### Шаг 4. Создать custom-format dump

```bash
pg_dump -U app_user -d app_db -Fc -f app_db.dump
```

### Шаг 5. Восстановить custom dump

```bash
createdb -U postgres restored_db
pg_restore -U postgres -d restored_db app_db.dump
```

### Шаг 6. Восстановить с очисткой объектов

```bash
pg_restore -U postgres -d restored_db --clean --if-exists app_db.dump
```

## Проверка результата

- `\dt` показывает восстановленные таблицы;
- ключевые таблицы имеют ожидаемое количество строк;
- приложение может подключиться к восстановленной базе;
- после восстановления при необходимости выполнен `ANALYZE`;

## Типовые ошибки и как думать

### Думать, что `pg_dump` сохраняет весь кластер

`pg_dump` работает с одной базой; глобальные роли и tablespaces требуют отдельного подхода.

### Восстанавливать в непустую базу без понимания конфликтов

могут быть ошибки существующих объектов.

### Не проверять dump

backup полезен только если восстановление реально проверено.

### Восстанавливать недоверенный dump

dump может содержать SQL, который будет выполнен.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 16.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Для простого backup PostgreSQL 16 используй `pg_dump -d app_db > app_db.sql`, создай пустую базу и восстанови через `psql -d restored_db -f app_db.sql`. Для гибкого восстановления используй `pg_dump -Fc` и `pg_restore`.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 16. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Backup and Restore`;
- `SQL Dump`;
- `pg_dump`;
- `pg_restore`;
- `psql`;
- `PITR`;
