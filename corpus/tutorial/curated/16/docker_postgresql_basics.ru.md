---
title: "Учебный запуск PostgreSQL 16 в Docker"
pg_version: "16"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "docker_postgresql_basics"
tags:
  - "Docker"
  - "PostgreSQL"
  - "container"
  - "development"
official_backing:
  - "https://www.postgresql.org/docs/16/tutorial-start.html"
  - "https://www.postgresql.org/docs/16/app-psql.html"
  - "https://www.postgresql.org/docs/16/runtime-config-connection.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Учебный запуск PostgreSQL 16 в Docker

## Назначение

Этот материал показывает базовый учебный сценарий запуска PostgreSQL в Docker: старт контейнера, подключение через `psql`, сохранение данных в volume и первичная диагностика через `docker logs`. Он нужен для локальной практики, лабораторных и быстрого воспроизводимого окружения.

## Когда использовать

- нужно быстро поднять "чистый" PostgreSQL для обучения;
- требуется изолированная среда без установки PostgreSQL в систему;
- нужно повторяемо воспроизвести пример для команды или студентов;
- нужно проверить SQL-скрипт на новой базе;
- нужно понять различия подключения "с хоста" и "внутри контейнера".

## Простое объяснение

Контейнер PostgreSQL — это отдельный процесс с собственной файловой системой и сетевым пространством. Переменные `POSTGRES_PASSWORD` и `POSTGRES_DB` на старте задают базовую инициализацию. Проброс порта `-p 5432:5432` делает сервер доступным с хоста.

Если данные важны, их нельзя оставлять только в writable-layer контейнера. Для сохранения между пересозданиями нужен Docker volume и монтирование в каталог данных PostgreSQL. Иначе удаление контейнера приведёт к потере данных.

## Предварительные условия

- установлен Docker и пользователь имеет право запускать контейнеры;
- порт 5432 свободен или выбран альтернативный порт;
- на хосте есть клиент `psql` для проверки подключения;
- понятна разница между учебным и production-сценарием;
- есть место на диске для volume.

## Минимальный рабочий пример

```bash
docker volume create pg_demo_data
```

```bash
docker run --name pg-demo \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=demo_db \
  -p 5432:5432 \
  -v pg_demo_data:/var/lib/postgresql/data \
  -d postgres:16
```

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d demo_db
```

```bash
docker exec -it pg-demo psql -U postgres -d demo_db
```

## Пошаговый алгоритм

1. Создай volume для сохранения данных между перезапусками.
2. Запусти контейнер с `POSTGRES_PASSWORD`, `POSTGRES_DB`, пробросом порта и volume.
3. Проверь состояние контейнера: `docker ps`.
4. Открой логи: `docker logs pg-demo` и дождись строки о готовности сервера.
5. Подключись с хоста через `psql -h -p -U -d`.
6. Проверь контекст: `SELECT current_database(), current_user;`.
7. При необходимости зайди внутрь контейнера и проверь `psql` локально через `docker exec`.
8. Останови/запусти контейнер повторно и убедись, что данные сохранились благодаря volume.

## Как проверить результат

```bash
docker ps --filter name=pg-demo
```

```bash
docker logs --tail 50 pg-demo
```

```sql
SELECT version();
SELECT current_database(), current_user;
```

```text
\l
\dt
```

- контейнер должен быть в состоянии `Up`;
- в логах должна быть готовность принимать подключения;
- `psql` с хоста и из контейнера должны подключаться к ожидаемой базе;
- после рестарта контейнера созданные таблицы/данные должны остаться.

## Типовые ошибки

- Порт занят локальным PostgreSQL или другим контейнером.
- Подключение идёт не к контейнеру, а к другому серверу на 5432.
- Удалён контейнер без сохранённого volume и данные потеряны.
- Неверный пароль/имя базы относительно `POSTGRES_PASSWORD`/`POSTGRES_DB`.
- Игнорирование `docker logs` при диагностике старта.

## Безопасность и ограничения

- Этот сценарий учебный; он не равен production-настройке PostgreSQL.
- Для production нужны отдельные требования: сеть, бэкапы, мониторинг, патчи, секреты, HA.
- Не храни реальные прод-данные в случайных локальных volume без политики доступа и резервного копирования.
- Публичный проброс порта требует контроля firewall и окружения.

## Что искать в official corpus

- `https://www.postgresql.org/docs/16/tutorial-start.html`
- `https://www.postgresql.org/docs/16/app-psql.html`
- `https://www.postgresql.org/docs/16/runtime-config-connection.html`

## Короткий вывод

Docker позволяет быстро поднять PostgreSQL для обучения и тестов, особенно в сочетании с `psql`. Ключевые элементы надёжного учебного запуска: корректные переменные инициализации, проверка логов и обязательный volume для данных. Этот подход удобен для практики, но не заменяет полноценную production-архитектуру.
