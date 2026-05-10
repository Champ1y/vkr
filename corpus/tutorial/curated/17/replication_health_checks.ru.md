---
title: "Проверка состояния репликации в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "replication_health_checks"
tags:
  - "monitoring"
  - "replication"
  - "pg_stat_replication"
  - "pg_stat_subscription"
official_backing:
  - "https://www.postgresql.org/docs/17/monitoring.html"
  - "https://www.postgresql.org/docs/17/logical-replication-monitoring.html"
  - "https://www.postgresql.org/docs/17/monitoring-stats.html"
  - "https://www.postgresql.org/docs/17/view-pg-replication-slots.html"
usage_rule: "Использовать только как вспомогательный учебный слой. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Проверка состояния репликации в PostgreSQL 17

## Назначение

Показать, как проверить, работает ли replication, и где искать признаки проблем.

Этот файл написан для режима `tutorial`. Он не заменяет официальную документацию PostgreSQL 17, а помогает объяснять её проще и пошагово.

## Простое объяснение

После настройки replication важно проверить не только наличие объектов, но и фактическую передачу изменений. Для этого смотрят системные представления статистики, replication slots, состояние subscription и тестовую запись.

## Когда использовать

- как проверить репликацию;
- данные не приходят;
- replication lag;
- pg_stat_subscription;
- pg_replication_slots;

## Предварительные условия

- репликация уже настроена;
- есть доступ к publisher и subscriber;
- есть тестовая таблица или безопасная тестовая запись;

## Пошаговая инструкция

### Шаг 1. На subscriber проверить subscription

```sql
SELECT subname, enabled FROM pg_subscription;
```

### Шаг 2. На subscriber посмотреть статистику

```sql
SELECT * FROM pg_stat_subscription;
```

### Шаг 3. На publisher проверить slots

```sql
SELECT slot_name, plugin, slot_type, active FROM pg_replication_slots;
```

### Шаг 4. На publisher проверить replication-подключения

```sql
SELECT pid, usename, application_name, client_addr, state FROM pg_stat_replication;
```

### Шаг 5. Сделать тестовую вставку на publisher

```sql
INSERT INTO public.products (name, price) VALUES ('replication_test', 1.00);
```

### Шаг 6. Проверить строку на subscriber

```sql
SELECT * FROM public.products WHERE name = 'replication_test';
```

## Проверка результата

- subscription включена;
- slot активен или понятно, почему он не активен;
- тестовая строка дошла до subscriber;
- логи не содержат ошибок применения изменений;

## Типовые ошибки и как думать

### Смотреть только `pg_subscription`

наличие subscription ещё не означает, что данные успешно применяются.

### Не проверять логи

конфликты и ошибки прав часто лучше видны в server logs.

### Долго держать неактивный slot

slot может удерживать WAL и увеличивать расход диска.

## Ограничения материала

- Этот файл не должен быть единственным источником фактического ответа.
- Для точного синтаксиса, параметров, ограничений и поведения нужно использовать official corpus PostgreSQL 17.
- Если найденный official-контекст слабый или относится к другой версии, система должна запросить уточнение или безопасно отказаться от уверенного ответа.
- Английские термины PostgreSQL, имена параметров, команд и файлов не переводятся: `psql`, `pg_hba.conf`, `CREATE ROLE`, `VACUUM`, `EXPLAIN`, `jsonb`.

## Короткий ответ для RAG

Чтобы проверить logical replication в PostgreSQL 17, смотри `pg_subscription` и `pg_stat_subscription` на subscriber, `pg_replication_slots` и `pg_stat_replication` на publisher, затем сделай тестовый `INSERT` на publisher и `SELECT` на subscriber.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `Monitoring Database Activity`;
- `Logical Replication / Monitoring`;
- `pg_stat_subscription`;
- `pg_stat_replication`;
- `pg_replication_slots`;
