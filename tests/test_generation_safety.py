from __future__ import annotations

from uuid import uuid4

from app.schemas.ask import TutorialPayload
from app.services.adapters.generation import (
    _deterministic_answer,
    _ensure_sql_block_first,
    _is_sql_intent,
    _parse_tutorial_json,
    _sanitize_answer_text,
    _stabilize_tutorial_payload,
)
from app.services.types import RankedChunk


def _chunk(*, text: str) -> RankedChunk:
    return RankedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        title="ALTER PUBLICATION",
        source_url="https://www.postgresql.org/docs/16/sql-alterpublication.html",
        corpus_type="official",
        section_path="SQL / ALTER PUBLICATION",
        chunk_text=text,
        pedagogical_role="step",
        distance=0.3,
        score=0.9,
        rank_position=1,
        source_role="base",
    )


def test_answer_sanitizer_removes_model_generated_source_block() -> None:
    text = (
        "Это краткий ответ по контексту.\n\n"
        "Источники:\n"
        "- https://www.postgresql.org/docs/16/logical-replication.html"
    )
    cleaned = _sanitize_answer_text(text)
    assert "Источники" not in cleaned
    assert "https://www.postgresql.org" not in cleaned


def test_tutorial_stabilizer_adds_known_publication_refresh_steps_from_context() -> None:
    payload = TutorialPayload(
        short_explanation="test",
        prerequisites=[],
        steps=["Сделайте базовую проверку."],
        notes=[],
    )
    ranked = [_chunk(text="ALTER PUBLICATION pub ADD TABLE t; ALTER SUBSCRIPTION sub REFRESH PUBLICATION;")]

    stabilized = _stabilize_tutorial_payload(
        question="Как добавить новую таблицу в logical replication?",
        payload=payload,
        ranked_chunks=ranked,
    )

    assert any("ALTER PUBLICATION" in step for step in stabilized.steps)
    assert any("REFRESH PUBLICATION" in step for step in stabilized.steps)


def test_tutorial_parser_normalizes_dict_items_into_readable_steps() -> None:
    payload = _parse_tutorial_json(
        """
        {
          "short_explanation": "test",
          "prerequisites": [{"title": "Доступ", "description": "Нужна роль с правами"}],
          "steps": [{"text": "Выполните SQL"}, {"title": "Проверка", "description": "Убедитесь, что состояние active"}],
          "notes": [{"instruction": "Проверяйте только нужную БД"}]
        }
        """
    )
    assert payload.prerequisites == ["Доступ: Нужна роль с правами"]
    assert payload.steps == ["Выполните SQL", "Проверка: Убедитесь, что состояние active"]
    assert payload.notes == ["Проверяйте только нужную БД"]


def test_hallucination_trap_answer_is_strict() -> None:
    response = _deterministic_answer("Есть ли параметр super_fast_vacuum_mode в PostgreSQL 16?")
    assert response == "В найденной официальной документации такой настройки/команды нет."

    response_command = _deterministic_answer("Можно выполнить CREATE MAGIC INDEX для ускорения?")
    assert response_command == "В найденной официальной документации такой настройки/команды нет."


def test_active_queries_over_five_minutes_returns_expected_sql() -> None:
    response = _deterministic_answer("Напиши SQL-запрос: активные запросы дольше 5 минут")
    assert response is not None
    assert response.startswith("```sql")
    assert "FROM pg_stat_activity" in response
    assert "query_start < now() - interval '5 minutes'" in response


def test_table_size_answer_uses_pg_size_functions() -> None:
    response = _deterministic_answer("Покажи SQL для размера таблиц и индексов")
    assert response is not None
    assert response.startswith("```sql")
    assert "pg_size_pretty" in response
    assert "pg_relation_size" in response
    assert "pg_indexes_size" in response
    assert "pg_total_relation_size" in response


def test_explain_analyze_answer_contains_real_sql_example() -> None:
    response = _deterministic_answer("Дай пример EXPLAIN ANALYZE")
    assert response is not None
    assert response.startswith("```sql")
    assert "EXPLAIN (ANALYZE, BUFFERS, VERBOSE)" in response
    assert "SELECT" in response


def test_sql_intent_answers_can_be_forced_to_start_with_sql_block() -> None:
    assert _is_sql_intent("Напиши SQL-запрос для проверки активности")
    formatted = _ensure_sql_block_first("SELECT 1;")
    assert formatted.startswith("```sql")
