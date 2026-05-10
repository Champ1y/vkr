---
title: "Обзор streaming replication в PostgreSQL 18"
pg_version: "18"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "streaming_replication_overview"
tags:
  - "streaming replication"
  - "physical replication"
  - "standby"
  - "WAL"
official_backing:
  - "https://www.postgresql.org/docs/18/warm-standby.html"
  - "https://www.postgresql.org/docs/18/different-replication-solutions.html"
  - "https://www.postgresql.org/docs/18/runtime-config-replication.html"
  - "https://www.postgresql.org/docs/18/high-availability.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Обзор streaming replication в PostgreSQL 18

## Назначение

Этот материал объясняет базовую картину physical streaming replication: что именно реплицируется, как читать состояние реплики и какие проверки обязательны перед запуском в production. Он закрывает вопросы "зачем нужна standby", "почему есть lag" и "чем physical replication отличается от logical replication".

## Когда использовать

- нужен HA-сценарий с быстрым переключением при отказе primary;
- нужна read replica для части read-нагрузки;
- необходимо иметь актуальную горячую копию базы для обслуживания и отчётов;
- требуется базовый runbook мониторинга репликации;
- нужно объяснить команде, почему physical replication не реплицирует выборочно отдельные таблицы.

## Простое объяснение

Streaming replication в PostgreSQL передаёт поток WAL-записей с primary на standby. Standby применяет WAL и восстанавливает то же физическое состояние данных, что и на primary. Это значит, что репликация идёт на уровне всего кластера, а не на уровне отдельных таблиц.

В practical-плане это удобно для отказоустойчивости: если primary недоступен, standby можно продвинуть в новый primary. Но сама по себе репликация не равна бэкапу на "любой момент": для восстановления на точку времени нужен отдельно настроенный архив WAL и процедуры PITR.

Важно различать physical и logical replication. Physical replication хороша для полной копии инстанса. Logical replication применяется для выборочного переноса объектов и более гибкой топологии обмена данными.

## Предварительные условия

- primary и standby доступны по сети с предсказуемой задержкой;
- настроен доступ для replication-соединения через `pg_hba.conf`;
- на primary заданы параметры репликации (`wal_level`, `max_wal_senders`, при необходимости `max_replication_slots`);
- создан replication role с минимально необходимыми правами;
- есть мониторинг lag и алерты, а также plan на failover/failback.

## Минимальный рабочий пример

```sql
SHOW wal_level;
SHOW max_wal_senders;
SHOW max_replication_slots;
```

```sql
SELECT application_name, client_addr, state, sync_state,
       write_lag, flush_lag, replay_lag
FROM pg_stat_replication;
```

```sql
SELECT pg_is_in_recovery();
```

```sql
SELECT status, conninfo, received_lsn, latest_end_lsn
FROM pg_stat_wal_receiver;
```

```sql
SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;
```

## Пошаговый алгоритм

1. Определи цель: только HA, HA + read scaling, или миграционный сценарий.
2. Проверь базовые параметры на primary и соответствие сетевых правил в `pg_hba.conf`.
3. Создай и проверь replication role, затем подними standby из согласованной базы (base backup).
4. Убедись, что standby подключился к primary и начал получать WAL.
5. На primary проверь строки в `pg_stat_replication` и состояние `state = streaming`.
6. На standby проверь `pg_is_in_recovery()` и состояние `pg_stat_wal_receiver`.
7. Оцени lag в единицах времени/LSN и проверь стабильность под реальной нагрузкой.
8. Зафиксируй процедуру failover и командные действия для on-call, включая post-failover проверки.

## Как проверить результат

```sql
SELECT application_name, state, sync_state,
       write_lag, flush_lag, replay_lag
FROM pg_stat_replication;
```

```sql
SELECT pg_is_in_recovery();
```

```sql
SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;
```

- на primary виден standby в `pg_stat_replication` со статусом `streaming`;
- на standby `pg_is_in_recovery()` возвращает `true`;
- lag не растёт бесконтрольно при нормальном workload;
- тестовая запись на primary появляется на standby в ожидаемое время.

## Типовые ошибки

- Путать physical replication и logical replication в требованиях проекта.
- Настроить реплику, но не мониторить lag и состояние `wal_receiver`.
- Не учитывать WAL retention и поведение replication slots.
- Считать реплику заменой бэкапа и не строить отдельную backup-стратегию.
- Применять DDL/maintenance без понимания влияния на lag и failover-готовность.

## Безопасность и ограничения

- Репликация передаёт весь WAL-поток, поэтому чувствительность данных и сетевую безопасность нужно учитывать на уровне инфраструктуры.
- Неправильные failover-действия могут привести к split-brain и потере согласованности.
- Репликация не защищает от логических ошибок приложения (например, массового `DELETE`), они тоже реплицируются.
- Для production обязательны регулярные учения failover и проверка recovery-процедур.
- За точными ограничениями параметров и режимов синхронности обращайся к official docs версии 18.

## Что искать в official corpus

- `https://www.postgresql.org/docs/18/warm-standby.html`
- `https://www.postgresql.org/docs/18/warm-standby.html`
- `https://www.postgresql.org/docs/18/different-replication-solutions.html`
- `https://www.postgresql.org/docs/18/runtime-config-replication.html`
- `https://www.postgresql.org/docs/18/runtime-config-replication.html`
- `https://www.postgresql.org/docs/18/high-availability.html`

## Короткий вывод

Streaming replication в PostgreSQL поддерживает физическую standby-копию через WAL и служит базой для HA-сценариев. Рабочая настройка состоит не только из параметров, но и из постоянной проверки `pg_stat_replication`/`pg_stat_wal_receiver` и контроля lag. Это мощный инструмент отказоустойчивости, но не замена полноценному backup и recovery-плану.
