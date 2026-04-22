from __future__ import annotations

from app.services.ingestion.chunker import TextChunker
from app.services.ingestion.parser import ParagraphBlock


def test_chunker_does_not_mix_different_sections() -> None:
    chunker = TextChunker(chunk_size=200, overlap=40)
    paragraphs = [
        ParagraphBlock(section_path="A / Intro", text="A " * 50, content_type="paragraph"),
        ParagraphBlock(section_path="B / Details", text="B " * 50, content_type="paragraph"),
    ]

    chunks = chunker.build_chunks(paragraphs)

    assert len(chunks) == 2
    assert chunks[0].section_path == "A / Intro"
    assert chunks[1].section_path == "B / Details"
