---
title: "Правила безопасной генерации ответов в tutorial-режиме PostgreSQL 17"
pg_version: "17"
language: "ru"
corpus_type: "supplementary"
source_role: "curated_learning"
audience_level: "beginner"
pedagogical_role: "tutorial"
topic: "safe_rag_answering_rules"
tags:
  - "RAG"
  - "grounding"
  - "sources"
  - "evidence guard"
  - "tutorial"
official_backing:
  - "https://www.postgresql.org/docs/17/index.html"
  - "https://www.postgresql.org/docs/17/release.html"
external_reference:
  []
usage_rule: "Использовать только как вспомогательный учебный слой для tutorial + extended_mode. Фактические утверждения должны подтверждаться official corpus выбранной версии."
---

# Правила безопасной генерации ответов в tutorial-режиме PostgreSQL 17

## Назначение

Этот документ задаёт практические правила для RAG-системы, чтобы ответы были одновременно понятными и проверяемыми: official-контент подтверждает факты, supplementary-контент объясняет. Цель — снизить риск галлюцинаций, смешивания версий и опасных советов для production.

## Когда использовать

- нужно определить policy поведения для режимов `answer`, `tutorial`, `tutorial+extended`;
- требуется формальный version guard по ветке PostgreSQL 17;
- система отвечает на вопросы про backup, security, replication, production config;
- нужно описать fallback, если official evidence недостаточен;
- требуется объяснить команде различие ролей official и supplementary корпусов.

## Простое объяснение

В этом проекте official corpus — источник истины (source of truth). Это означает: любое фактическое утверждение о синтаксисе, параметрах, ограничениях и поведении PostgreSQL должно иметь опору в official docs выбранной версии.

Supplementary corpus — учебный слой. Он полезен для "человеческого" объяснения, пошаговых примеров и типовых ошибок, но не может быть единственным доказательством фактов. Если official evidence нет, система должна снижать уверенность, задавать уточнение или явно отказываться от категоричного ответа.

Version guard — обязательный фильтр: для вопросов по PostgreSQL 17 retrieval должен приоритизировать и подтверждать факты через ветку `/docs/17/`. Evidence guard — проверка, что ключевые утверждения в финальном ответе действительно опираются на найденные official фрагменты, а не только на похожесть embedding.

## Предварительные условия

- в индексе документов хранится метадата `pg_version`, `corpus_type`, `source_role`, `topic`;
- роутер режимов знает policy для `answer`, `tutorial`, `tutorial+extended`;
- retriever умеет version-aware фильтрацию;
- генератор может понижать уверенность и отдавать fallback при слабой доказательной базе;
- есть шаблоны ответа для high-risk тем с обязательными предупреждениями.

## Минимальный рабочий пример

```text
mode=answer
  allowed_corpus_type = official

mode=tutorial, extended_mode=false
  allowed_corpus_type = official

mode=tutorial, extended_mode=true
  allowed_corpus_type = official + supplementary
```

```text
version_guard:
  target_pg_version = 17
  official_docs_branch = /docs/17/
```

```text
evidence_guard:
  final factual claims must be backed by official evidence
  supplementary can rephrase/explain only
```

## Пошаговый алгоритм

1. Определи режим запроса: `answer`, `tutorial`, `tutorial+extended`.
2. Примени policy по разрешённым типам корпуса для выбранного режима.
3. Включи version guard и отфильтруй контент под PostgreSQL 17.
4. Сначала собери official evidence для ключевых фактов.
5. Если `extended_mode=true`, добавь supplementary как объяснение и практический контекст.
6. Запусти evidence guard: проверь, что фактические claims имеют official backing.
7. Для high-risk тем добавь предупреждения и консервативный тон (без рискованных "универсальных" советов).
8. Если official evidence слабый или противоречивый, отдай fallback: уточнение, ограниченный ответ или безопасный отказ от уверенного утверждения.

## Как проверить результат

```text
Checklist перед финальным ответом:
1) Есть ли минимум один релевантный official фрагмент на каждый ключевой факт?
2) Совпадает ли версия (ветка /docs/17/)?
3) Не используется ли supplementary как единственная опора для фактов?
4) Есть ли явные оговорки для production-risk операций?
```

```text
Пример fallback:
"Не вижу достаточного official подтверждения для версии 17. Уточните целевой параметр/сценарий, и я сверю по official docs."
```

- в итоговом ответе видна связь ключевых фактов с official source;
- нет кросс-версийных подстановок;
- supplementary используется для понятности, а не для замены доказательств;
- high-risk ответы содержат ограничения и шаги проверки.

## Типовые ошибки

- Отвечать уверенно только на основе curated/supplementary текста.
- Ослаблять version guard и смешивать разные ветки документации.
- Пропускать evidence guard, если semantic search дал "похожий" фрагмент.
- Давать рискованные production-советы без предупреждений и валидации.
- Путать учебное объяснение с нормативным источником факта.

## Безопасность и ограничения

- Темы backup, security, replication, production config считаются high-risk и требуют повышенного порога доказательности.
- Если official evidence отсутствует, система должна быть консервативной: не выдумывать синтаксис и не обещать поведение.
- Даже корректный технически ответ может быть опасен без контекста инфраструктуры; нужны уточнения по окружению.
- RAG-пайплайн с vector retrieval не заменяет policy-контроль, evidence guard и human review для критичных изменений.

## Что искать в official corpus

- `https://www.postgresql.org/docs/17/index.html`
- `https://www.postgresql.org/docs/17/release.html`
- `https://www.postgresql.org/docs/17/backup.html`
- `https://www.postgresql.org/docs/17/high-availability.html`
- `https://www.postgresql.org/docs/17/runtime-config.html`

## Короткий вывод

Безопасный tutorial-ответ в RAG строится на простом принципе: official docs подтверждают факты, supplementary помогает объяснить. Version guard и evidence guard обязательны, особенно в high-risk темах вроде backup, security и replication. Если доказательств недостаточно, корректный fallback лучше, чем уверенная, но непроверенная рекомендация.
