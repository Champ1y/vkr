---
title: "Как отменить или завершить запрос в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "cancel_terminate_queries"
tags:
  - "pg_cancel_backend"
  - "pg_terminate_backend"
  - "monitoring"
  - "admin"
official_backing:
  - "https://www.postgresql.org/docs/17/functions-admin.html"
  - "https://www.postgresql.org/docs/17/monitoring.html"
  - "https://www.postgresql.org/docs/17/monitoring-stats.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Как отменить или завершить запрос в PostgreSQL 17

## Назначение

Этот материал объясняет безопасный порядок действий, когда нужно остановить проблемный запрос: сначала `pg_cancel_backend`, затем при необходимости `pg_terminate_backend`. Он помогает не повредить рабочую нагрузку и не прервать важные служебные операции по ошибке.

## Когда использовать

- запрос выполняется слишком долго и мешает другим операциям;
- есть блокировка, которая держится дольше допустимого;
- сессия зависла в приложении и не освобождает ресурсы;
- нужно быстро снять инцидент по перегрузке;
- требуется runbook для on-call и DBA-процедур.

## Простое объяснение

`pg_cancel_backend(pid)` отправляет сигнал отмены текущего запроса, но соединение остаётся открытым. Это более мягкое действие и обычно первая попытка. `pg_terminate_backend(pid)` завершает весь backend-процесс сессии; незакоммиченная транзакция откатывается, а клиенту возвращается ошибка соединения.

Практический принцип простой: сначала убедиться, что PID действительно проблемный и не относится к критичной операции (backup, migration, maintenance), затем попробовать cancel, и только после этого — terminate при явной необходимости.

## Предварительные условия

- есть доступ к `pg_stat_activity`;
- есть права на отправку сигналов (обычно superuser или роль с соответствующими привилегиями, например `pg_signal_backend`);
- есть связь с владельцем приложения/сервиса;
- есть критерий, что считается "слишком долго" для конкретного сценария;
- есть журнал действий для incident response.

## Минимальный рабочий пример

```sql
SELECT pid, usename, application_name, state,
       wait_event_type, wait_event,
       now() - query_start AS duration,
       query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY duration DESC;
```

```sql
SELECT pg_cancel_backend(12345);
```

```sql
SELECT pg_terminate_backend(12345);
```

## Пошаговый алгоритм

1. Найди кандидата по длительности, состоянию и эффекту на систему.
2. Проверь владельца (`usename`, `application_name`) и назначение запроса.
3. Убедись, что это не критичный системный процесс и не плановая админ-операция.
4. Выполни `pg_cancel_backend(pid)` как первый шаг.
5. Подожди короткий интервал и перепроверь `pg_stat_activity`.
6. Если запрос не прекращается или сессия блокирует других, примени `pg_terminate_backend(pid)`.
7. После terminate проверь откат транзакции, состояние приложения и повторные попытки клиента.
8. Зафиксируй действие и причину для postmortem.

## Как проверить результат

```sql
SELECT pid, state, wait_event_type, wait_event, now() - query_start AS duration
FROM pg_stat_activity
WHERE pid = 12345;
```

```sql
SELECT pid, usename, state, now() - query_start AS duration
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY duration DESC;
```

- после `pg_cancel_backend` целевой запрос должен исчезнуть из активных или сменить состояние;
- после `pg_terminate_backend` целевой PID обычно пропадает из `pg_stat_activity`;
- связанные блокировки и очередь ожидания должны уменьшиться;
- приложение должно корректно обработать ошибку и восстановить работу.

## Типовые ошибки

- Завершить не тот PID из-за спешки и отсутствия верификации.
- Сразу использовать terminate, пропуская более мягкий cancel.
- Убить процесс backup/migration и получить непредсказуемые последствия.
- Не предупредить владельца сервиса и создать каскадные ретраи в приложении.
- Не проверить состояние системы после вмешательства.

## Безопасность и ограничения

- `pg_terminate_backend` может откатить длинную транзакцию и вызвать всплеск повторных попыток в приложении.
- Массовое завершение сессий без диагностики усугубляет инцидент.
- Решение об остановке запросов в production должно учитывать SLA и бизнес-критичность операции.
- Учебный материал не заменяет официальные ограничения по правам и системным процессам.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/functions-admin.html`
- `https://www.postgresql.org/docs/17/monitoring.html`
- `https://www.postgresql.org/docs/17/monitoring-stats.html`
- `https://www.postgresql.org/docs/17/monitoring.html`

## Короткий вывод

Безопасная остановка запроса в PostgreSQL строится по принципу "от мягкого к жёсткому": сначала `pg_cancel_backend`, затем `pg_terminate_backend` только при необходимости. Ключ к безошибочному действию — точная идентификация PID и понимание контекста нагрузки. После любого вмешательства обязательно проверяют последствия для блокировок, транзакций и приложения.
