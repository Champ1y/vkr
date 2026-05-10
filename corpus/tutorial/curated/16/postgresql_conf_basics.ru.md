---
title: "Основы postgresql.conf и ALTER SYSTEM в PostgreSQL 16"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "postgresql_conf_basics"
tags:
  - "postgresql.conf"
  - "configuration"
  - "ALTER SYSTEM"
  - "pg_settings"
  - "reload"
official_backing:
  - "https://www.postgresql.org/docs/16/runtime-config.html"
  - "https://www.postgresql.org/docs/16/config-setting.html"
  - "https://www.postgresql.org/docs/16/view-pg-settings.html"
  - "https://www.postgresql.org/docs/16/sql-altersystem.html"
external_reference:
  - "https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server"
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Основы postgresql.conf и ALTER SYSTEM в PostgreSQL 16

## Назначение

Этот материал помогает безопасно менять конфигурацию PostgreSQL: понимать, где хранится параметр, как применяются изменения и чем отличаются `reload` и `restart`. Он закрывает частые вопросы новичков: почему параметр "не применился", откуда взялось текущее значение и почему после `ALTER SYSTEM` конфигурация отличается от ожидаемой.

## Когда использовать

- нужно изменить параметр в `postgresql.conf` или через `ALTER SYSTEM`;
- после тюнинга требуется проверить, применились ли новые значения;
- нужно понять, почему в `pg_settings` одно значение, а в файле другое;
- перед troubleshooting производительности или логирования;
- при подготовке изменений для production через change-процедуру.

## Простое объяснение

У PostgreSQL несколько уровней конфигурации. Параметр можно задать в конфигурационных файлах, через `ALTER SYSTEM`, на уровне базы (`ALTER DATABASE`), роли (`ALTER ROLE`) и даже на уровне текущей сессии. Поэтому практический вопрос не только "какое значение у параметра", но и "какой источник этого значения". Основная рабочая точка для диагностики — `pg_settings`: там видно текущее значение, контекст применения и флаг `pending_restart`.

`ALTER SYSTEM` удобен тем, что пишет значение в `postgresql.auto.conf` и не требует ручного редактирования файла. Но это не отменяет дисциплину: изменения должны быть зафиксированы, проверены и согласованы, особенно для параметров с контекстом `postmaster`, которые требуют перезапуска процесса PostgreSQL.

## Предварительные условия

- есть доступ к `psql` и права на просмотр системных представлений;
- для `ALTER SYSTEM` обычно нужны повышенные права (часто superuser);
- понятно, какой инстанс и какая среда изменяются (dev/stage/prod);
- есть окно обслуживания, если параметр требует `restart`;
- есть план отката и журнал изменений конфигурации.

## Минимальный рабочий пример

```sql
SHOW config_file;
SHOW hba_file;
SHOW data_directory;

SELECT name, setting, unit, context, source, pending_restart
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'log_min_duration_statement');

ALTER SYSTEM SET log_min_duration_statement = '500ms';
SELECT pg_reload_conf();

SELECT name, setting, source, pending_restart
FROM pg_settings
WHERE name = 'log_min_duration_statement';
```

## Пошаговый алгоритм

1. Зафиксируй текущее состояние: снимок `SHOW` и нужных строк из `pg_settings`.
2. Определи область изменения: параметр должен жить в файле, в `ALTER SYSTEM`, на уровне роли или базы.
3. Проверь `context` в `pg_settings`, чтобы заранее знать, нужен `reload` или `restart`.
4. Внеси изменение одним способом, без смешивания нескольких источников одновременно.
5. Выполни `SELECT pg_reload_conf();` для параметров, поддерживающих `SIGHUP`.
6. Если у параметра `pending_restart = true`, запланируй controlled restart.
7. После применения ещё раз сравни `setting`, `source` и поведение workload.
8. Документируй изменение: что меняли, зачем и как проверили эффект.

## Как проверить результат

```sql
SELECT name, setting, source, context, pending_restart
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'log_min_duration_statement');
```

```sql
SHOW log_min_duration_statement;
```

- `source` должен указывать ожидаемый источник (`configuration file`, `override`, и т.д.);
- `pending_restart = false` означает, что параметр применён без обязательного рестарта;
- при изменении логирования проверь, что в логах появились записи в ожидаемом формате и объёме.

## Типовые ошибки

- Менять параметр и забывать применить `reload`/`restart`.
- Вводить значение без единиц (`MB`, `ms`) и получать неожиданный результат.
- Смешивать правки в файле и `ALTER SYSTEM`, а потом не понимать, какой источник победил.
- Копировать чужие tuning-наборы без измерений и baseline.
- Проверять только файл, но не смотреть фактические значения в `pg_settings`.

## Безопасность и ограничения

- Конфигурация в production меняется по change-процедуре, с окном отката.
- Агрессивные настройки памяти и параллелизма могут ухудшить стабильность под нагрузкой.
- `ALTER SYSTEM` меняет глобальное поведение инстанса, а не одной сессии.
- Этот материал объясняет подход, но не заменяет точную справку по параметрам.
- Факты по допустимым диапазонам и контексту применения нужно сверять с official docs версии 16.

## Что искать в official corpus

- `https://www.postgresql.org/docs/16/runtime-config.html`
- `https://www.postgresql.org/docs/16/config-setting.html`
- `https://www.postgresql.org/docs/16/view-pg-settings.html`
- `https://www.postgresql.org/docs/16/sql-altersystem.html`

## Короткий вывод

Работа с конфигурацией PostgreSQL начинается не с редактирования файла, а с чтения `pg_settings`: текущего значения, источника и контекста параметра. Сначала выбирают правильный уровень настройки, затем применяют `reload` или `restart` по требованиям параметра. Любое изменение в production должно сопровождаться проверкой результата и понятным планом отката.
