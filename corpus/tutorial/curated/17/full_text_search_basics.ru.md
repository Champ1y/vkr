---
title: "Основы полнотекстового поиска в PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "full_text_search_basics"
tags:
  - "full text search"
  - "tsvector"
  - "tsquery"
  - "GIN"
official_backing:
  - "https://www.postgresql.org/docs/17/textsearch.html"
  - "https://www.postgresql.org/docs/17/textsearch-controls.html"
  - "https://www.postgresql.org/docs/17/textsearch-tables.html"
  - "https://www.postgresql.org/docs/17/textsearch-indexes.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Основы полнотекстового поиска в PostgreSQL 17

## Назначение

Этот материал показывает, как запустить Full Text Search (FTS) в PostgreSQL: от подготовки текста до индекса и ранжирования результата. Он нужен, когда пользователь хочет делать быстрый поиск по словам и фразам внутри базы без внешнего поискового движка.

## Когда использовать

- нужно искать по статьям, описаниям, комментариям, справочным текстам;
- `LIKE '%...%'` уже медленный и плохо масштабируется;
- нужен лексический поиск с учётом нормализации слов;
- в RAG нужен lexical-канал для hybrid retrieval вместе с vector search;
- требуется ранжирование результатов по релевантности.

## Простое объяснение

FTS в PostgreSQL состоит из двух частей: документ (`tsvector`) и запрос (`tsquery`). `tsvector` содержит нормализованные лексемы, а `tsquery` описывает, что ищем. Оператор `@@` проверяет совпадение. Для скорости обычно используют GIN-индекс.

Ключевая идея: FTS не сравнивает "сырой текст строкой", как `LIKE`, а работает со словарями и токенами. Поэтому важно выбрать языковую конфигурацию (`english`, `russian` и т.д.) под реальный язык данных. Неправильная конфигурация снижает качество поиска даже при хорошем индексе.

## Предварительные условия

- есть таблица с текстовыми полями (`title`, `body`, `content`);
- выбран язык для конфигурации FTS;
- понятен сценарий поиска: отдельные слова, фразы, AND/OR;
- есть право создавать индексы;
- есть план проверки релевантности на реальных пользовательских запросах.

## Минимальный рабочий пример

```sql
SELECT to_tsvector('english', 'PostgreSQL is a powerful database')
       @@ plainto_tsquery('english', 'powerful database');
```

```sql
CREATE INDEX IF NOT EXISTS articles_fts_idx
ON articles
USING gin (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, '')));
```

```sql
SELECT id,
       ts_rank(
           to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, '')),
           plainto_tsquery('english', 'database performance')
       ) AS rank
FROM articles
WHERE to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
      @@ plainto_tsquery('english', 'database performance')
ORDER BY rank DESC
LIMIT 20;
```

## Пошаговый алгоритм

1. Определи, какие поля участвуют в поиске, и какой язык реально в данных.
2. Собери выражение `to_tsvector(...)` для этих полей с `coalesce`, чтобы избежать `NULL`-проблем.
3. Создай GIN-индекс на том же выражении, которое будет в `WHERE`.
4. Запускай поиск через `plainto_tsquery` для обычных пользовательских фраз.
5. Для более сложных сценариев добавляй `to_tsquery` или `websearch_to_tsquery`.
6. Сортируй результаты по `ts_rank` и валидируй релевантность на примерах из продукта.
7. При изменении языка/домена текста повторно проверь конфигурацию и качество выдачи.

## Как проверить результат

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM articles
WHERE to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
      @@ plainto_tsquery('english', 'database performance');
```

```sql
SELECT id,
       ts_rank(
         to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, '')),
         plainto_tsquery('english', 'database performance')
       ) AS rank
FROM articles
ORDER BY rank DESC
LIMIT 10;
```

- в плане запроса должен использоваться GIN-индекс для FTS-выражения;
- время поиска должно быть стабильным на реальном объёме данных;
- top-N результатов должны быть семантически ожидаемыми для пользователя.

## Типовые ошибки

- Применять `LIKE '%word%'` на больших таблицах вместо FTS.
- Создать индекс на одно выражение, а в запросе использовать другое.
- Выбрать `english` для русскоязычного корпуса без проверки качества.
- Игнорировать ранжирование и отдавать "первые попавшиеся" строки.
- Считать FTS прямой заменой vector retrieval в RAG-задачах.

## Безопасность и ограничения

- FTS не понимает смысл текста как embedding-модели; это лексический механизм.
- Морфология и стоп-слова зависят от конфигурации и домена текстов.
- Индекс FTS увеличивает объём хранения и стоимость записи.
- В production проверяй качество выдачи на реальных запросах, а не на синтетических строках.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/textsearch.html`
- `https://www.postgresql.org/docs/17/textsearch-controls.html`
- `https://www.postgresql.org/docs/17/textsearch-tables.html`
- `https://www.postgresql.org/docs/17/textsearch-indexes.html`

## Короткий вывод

Full Text Search в PostgreSQL строится вокруг пары `tsvector`/`tsquery` и обычно ускоряется GIN-индексом. Качество поиска определяется не только индексом, но и правильной языковой конфигурацией и ранжированием. Для RAG FTS полезен как lexical-компонент в hybrid-подходе, а не как замена embeddings.
