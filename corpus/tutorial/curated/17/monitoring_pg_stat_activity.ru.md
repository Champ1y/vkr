---
title: "Мониторинг активных запросов через pg_stat_activity в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "monitoring_pg_stat_activity"
tags:
  - "monitoring"
  - "pg_stat_activity"
  - "sessions"
  - "queries"
official_backing:
  - "https://www.postgresql.org/docs/17/monitoring.html"
  - "https://www.postgresql.org/docs/17/monitoring-stats.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Мониторинг активных запросов через pg_stat_activity в PostgreSQL 17

## Назначение

Этот материал учит быстро читать `pg_stat_activity` и принимать первичное решение при инцидентах: ждать, диагностировать глубже или аккуратно останавливать проблемный запрос. Он закрывает типичные вопросы "кто сейчас грузит базу", "почему всё зависло" и "что означает wait event".

## Когда использовать

- есть жалобы на медленную работу приложения;
- наблюдаются таймауты или очередь запросов;
- нужно найти долгие или зависшие транзакции;
- требуется проверить `idle in transaction`;
- перед применением `pg_cancel_backend` или `pg_terminate_backend`.

## Простое объяснение

`pg_stat_activity` показывает живую картину сессий PostgreSQL: кто подключён, что выполняет, как долго выполняет и чего ждёт. Это не полная диагностика всех проблем, но именно с этого представления обычно начинается расследование.

Ключевые поля для старта: `pid`, `usename`, `datname`, `state`, `query_start`, `xact_start`, `wait_event_type`, `wait_event`, `query`. Важно отличать `idle` от `idle in transaction`: первое чаще нормальное состояние пула подключений, второе может удерживать ресурсы и мешать autovacuum.

## Предварительные условия

- есть доступ к `psql` и права на чтение статистики;
- известен нормальный профиль нагрузки (что обычно считается "долго");
- есть связь с командой приложения для уточнения легитимности долгих операций;
- есть понимание, что мониторинг — это начало, а не финальный диагноз.

## Минимальный рабочий пример

```sql
SELECT pid, usename, datname, state,
       wait_event_type, wait_event,
       query_start, now() - query_start AS query_duration,
       query
FROM pg_stat_activity
WHERE backend_type = 'client backend'
ORDER BY query_start NULLS LAST;
```

```sql
SELECT pid, usename, now() - xact_start AS xact_duration, state, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY xact_duration DESC;
```

## Пошаговый алгоритм

1. Сними общий снимок `pg_stat_activity`, исключив технические фоновые процессы.
2. Отсортируй запросы по длительности и выдели самые долгие.
3. Проверь `wait_event_type/wait_event`, чтобы понять, идёт выполнение или ожидание ресурса.
4. Отдельно проверь `idle in transaction` и длительность транзакции.
5. Сопоставь `usename`, `application_name` и `datname` с владельцем нагрузки.
6. Для подозрительных сессий собери дополнительный контекст (например, блокировки или план запроса).
7. Прими действие: наблюдать, ограничить источник нагрузки, отменить запрос или эскалировать.
8. После действия повтори снимок и убедись, что симптом ушёл.

## Как проверить результат

```sql
SELECT pid, state, wait_event_type, wait_event,
       now() - query_start AS duration,
       usename, application_name
FROM pg_stat_activity
WHERE backend_type = 'client backend'
ORDER BY duration DESC NULLS LAST;
```

```sql
SELECT count(*) AS idle_in_tx_count
FROM pg_stat_activity
WHERE state = 'idle in transaction';
```

- количество "подозрительно долгих" сессий снизилось;
- проблемные `wait_event` исчезли или сократились по длительности;
- после remediation не появилось нового всплеска таймаутов на уровне приложения.

## Типовые ошибки

- Считать любой `idle` признаком проблемы.
- Игнорировать `wait_event` и смотреть только длительность.
- Реагировать на PID без проверки пользователя и `application_name`.
- Не различать долгий запрос и долгую транзакцию.
- Делать вывод по одному снимку вместо серии наблюдений.

## Безопасность и ограничения

- `query` может содержать чувствительные данные; доступ к мониторингу должен быть ограничен.
- Нельзя автоматически "убивать всё длиннее N секунд" без контекста бизнес-операций.
- Мониторинг сам по себе не объясняет первопричину; иногда нужно идти в планы, блокировки и параметры.
- Для production фиксируй действия и решения в incident timeline.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/monitoring.html`
- `https://www.postgresql.org/docs/17/monitoring-stats.html`
- `https://www.postgresql.org/docs/17/monitoring-stats.html`
- `https://www.postgresql.org/docs/17/monitoring.html`

## Короткий вывод

`pg_stat_activity` — главный вход в диагностику "что происходит прямо сейчас" в PostgreSQL. Смотри не только на длительность, но и на состояние, ожидания и владельца сессии. Решение о вмешательстве принимают только после проверки контекста и повторного контроля результата.
