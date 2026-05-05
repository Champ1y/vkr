---
title: "pgvector и хранение эмбеддингов для RAG-проекта на PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "pgvector_for_rag_project"
tags:
  - "pgvector"
  - "embeddings"
  - "RAG"
  - "vector search"
  - "ivfflat"
official_backing:
  - "https://www.postgresql.org/docs/17/extend-extensions.html"
  - "https://www.postgresql.org/docs/17/sql-createextension.html"
  - "https://www.postgresql.org/docs/17/indexes.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# pgvector и хранение эмбеддингов для RAG-проекта на PostgreSQL 17

## Назначение

Этот материал связывает PostgreSQL и практическую архитектуру RAG: как хранить документы, chunks, embeddings и метаданные, чтобы retrieval был управляемым и воспроизводимым. Он нужен, когда команда начинает строить semantic search в БД и хочет избежать типичных ошибок с версиями, моделью embedding и source-of-truth.

## Когда использовать

- нужно хранить текстовые chunks и их vectors внутри PostgreSQL;
- требуется фильтрация retrieval по версии документации и типу корпуса;
- нужно объяснить, зачем пересчитывать embeddings после смены модели;
- нужно собрать базовый SQL-пайплайн similarity search;
- в RAG-ответах важно разделять official и supplementary контент.

## Простое объяснение

RAG обычно хранит:
1. исходные документы;
2. chunks (фрагменты для поиска);
3. embeddings (векторное представление chunks);
4. метаданные для фильтрации и guard-правил.

`pgvector` добавляет тип `vector` и операторы похожести, позволяя делать nearest-neighbor search внутри PostgreSQL. Но vector retrieval — это только часть цепочки. Чтобы ответ был безопасным, нужны version guard, evidence guard и контроль источников. Вектор сам по себе не знает, какой источник authoritative и какую версию PostgreSQL выбрал пользователь.

Для этого полезно хранить метаданные рядом с chunk: `pg_version`, `corpus_type`, `source_role`, `topic`, URL источника. Тогда retriever может сначала фильтровать релевантное подмножество (`pg_version=17`, `corpus_type='official'`), а уже потом считать similarity.

## Предварительные условия

- установлен extension `vector` (`CREATE EXTENSION` доступен);
- определена embedding-модель и её размерность;
- есть схема таблиц documents/chunks/embeddings;
- определены правила version guard и source-priority;
- есть стратегия переиндексации/пересчёта embeddings при смене модели.

## Минимальный рабочий пример

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

```sql
CREATE TABLE documents (
    id uuid PRIMARY KEY,
    title text NOT NULL,
    source_url text NOT NULL,
    pg_version text NOT NULL,
    corpus_type text NOT NULL,
    source_role text NOT NULL,
    topic text NOT NULL
);

CREATE TABLE chunks (
    id uuid PRIMARY KEY,
    document_id uuid NOT NULL REFERENCES documents(id),
    chunk_text text NOT NULL,
    chunk_order integer NOT NULL
);

CREATE TABLE embeddings (
    id uuid PRIMARY KEY,
    chunk_id uuid NOT NULL REFERENCES chunks(id),
    model_name text NOT NULL,
    embedding vector(768) NOT NULL
);
```

```sql
CREATE INDEX embeddings_embedding_idx
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

```sql
SELECT c.id, c.chunk_text,
       e.embedding <=> $1::vector AS distance
FROM embeddings e
JOIN chunks c ON c.id = e.chunk_id
JOIN documents d ON d.id = c.document_id
WHERE d.pg_version = '17'
  AND d.corpus_type IN ('official', 'supplementary')
  AND e.model_name = 'text-embedding-3-large'
ORDER BY e.embedding <=> $1::vector
LIMIT 10;
```

## Пошаговый алгоритм

1. Создай extension `vector` и зафиксируй размерность `vector(N)` под конкретную модель.
2. Раздели данные на `documents`, `chunks`, `embeddings`, чтобы у каждого слоя была своя ответственность.
3. Добавь обязательные метаданные: `pg_version`, `corpus_type`, `source_role`, `topic`.
4. При индексации записывай `model_name`, чтобы отличать embeddings разных моделей.
5. Перед similarity search всегда фильтруй по version guard (`pg_version='17'`).
6. При формировании ответа применяй source policy: official — как factual backing, supplementary — как учебное объяснение.
7. Если меняется embedding model или размерность, пересчитай embeddings и обнови индекс.
8. После retrieval добавляй evidence guard: проверяй, что ключевые факты подтверждаются official-контентом.

## Как проверить результат

```sql
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

```sql
SELECT d.pg_version, d.corpus_type, d.source_role, count(*)
FROM documents d
GROUP BY d.pg_version, d.corpus_type, d.source_role
ORDER BY d.pg_version, d.corpus_type;
```

```sql
SELECT c.id, d.pg_version, d.corpus_type,
       e.embedding <=> $1::vector AS distance
FROM embeddings e
JOIN chunks c ON c.id = e.chunk_id
JOIN documents d ON d.id = c.document_id
WHERE d.pg_version = '17'
ORDER BY e.embedding <=> $1::vector
LIMIT 5;
```

- `vector` extension установлен и доступен;
- записи корректно фильтруются по версии PostgreSQL;
- similarity search возвращает осмысленные chunks;
- в ответах есть подтверждение factual-части через official corpus.

## Типовые ошибки

- Не хранить `pg_version` и смешивать контент разных веток документации.
- Сменить embedding model и оставить старые vectors без пересчёта.
- Хранить только vector без source metadata и терять управляемость retrieval.
- Считать vector search достаточным без evidence guard и reranking.
- Давать supplementary-контенту подменять роль official source.

## Безопасность и ограничения

- Vector similarity не гарантирует фактическую корректность ответа.
- Retrieval без version guard может привести к кросс-версийным конфликтам фактов.
- IVFFLAT требует корректной настройки и регулярного контроля качества поиска.
- Для чувствительных сценариев (backup/security/replication) ответ должен опираться на official evidence даже при хорошем semantic match.
- Этот материал обучающий; точные детали extension и индексации проверяй в official docs.

## Версионная привязка

Этот материал является учебным объяснением для PostgreSQL 17. Общая последовательность действий может совпадать между major-версиями, но точный синтаксис, ограничения, параметры и изменения поведения должны проверяться по official corpus выбранной версии. При сравнении версий нужно дополнительно использовать release notes PostgreSQL.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/extend-extensions.html`
- `https://www.postgresql.org/docs/17/sql-createextension.html`
- `https://www.postgresql.org/docs/17/indexes.html`

## Короткий вывод

`pgvector` позволяет хранить embeddings и выполнять similarity search прямо в PostgreSQL, что удобно для RAG-пайплайна. Но качество и безопасность ответа определяются не только nearest-neighbor поиском, а метаданными, version guard и evidence guard. Official corpus остаётся source of truth, а supplementary служит объяснительным слоем.
