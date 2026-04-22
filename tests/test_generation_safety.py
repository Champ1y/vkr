from __future__ import annotations

from uuid import uuid4

from app.schemas.ask import TutorialPayload
from app.services.adapters.generation import _sanitize_answer_text, _stabilize_tutorial_payload
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
