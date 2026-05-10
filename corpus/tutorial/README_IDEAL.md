# Ideal PostgreSQL Tutorial Supplementary Corpus

Готовый supplementary-корпус для `tutorial`.

## Структура

```text
tutorial/
├── curated/
│   ├── 16/
│   ├── 17/
│   └── 18/
├── html/                  # raw HTML archive (НЕ индексировать напрямую)
├── processed_html/        # cleaned markdown для embeddings
├── external_registry/
└── scripts/
```

## Ключевая политика ingestion

- `curated/**/*.md` индексируется как supplementary learning layer.
- `processed_html/**/*.md` индексируется как cleaned external supplementary.
- `html/**/*.html` хранится как source archive и **не индексируется напрямую**.
- factual-ответы должны подтверждаться official PostgreSQL docs выбранной major-версии.

См. [external_registry/ingestion_policy.json](external_registry/ingestion_policy.json).

## Проверки

Из корня проекта:

```bash
python3 corpus/tutorial/scripts/validate_tutorial_corpus.py corpus/tutorial
python3 corpus/tutorial/scripts/clean_html_for_ingestion.py corpus/tutorial
python3 corpus/tutorial/scripts/validate_processed_html.py corpus/tutorial
python3 corpus/tutorial/scripts/generate_quality_report.py corpus/tutorial
```

## Принцип версионности

Curated-материалы могут иметь одинаковую учебную структуру для 16/17/18.
Это нормально для supplementary слоя. Version-specific факты, параметры и поведение
должны подтверждаться official corpus выбранной версии (`/docs/16/`, `/docs/17/`, `/docs/18/`) и release notes.
