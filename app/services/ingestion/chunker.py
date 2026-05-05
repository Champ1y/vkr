from __future__ import annotations

import re
from dataclasses import dataclass

from app.db.enums import PedagogicalRole
from app.services.ingestion.parser import ParagraphBlock


@dataclass(slots=True)
class ChunkDraft:
    chunk_index: int
    section_path: str
    chunk_text: str
    token_count: int
    content_type: str
    pedagogical_role: str


_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-я0-9_]+")


def _infer_role(text: str) -> str:
    content = text.lower()
    if any(marker in content for marker in ["warning", "caution", "важно", "ошиб", "огранич"]):
        return PedagogicalRole.WARNING.value
    if any(marker in content for marker in ["example", "например", "пример"]):
        return PedagogicalRole.EXAMPLE.value
    if any(marker in content for marker in ["prerequisite", "предвар", "requirements", "необходимо"]):
        return PedagogicalRole.PREREQUISITE.value
    if any(marker in content for marker in ["step", "шаг", "далее", "затем", "после этого"]):
        return PedagogicalRole.STEP.value
    return PedagogicalRole.OVERVIEW.value


class TextChunker:
    def __init__(self, *, chunk_size: int, overlap: int) -> None:
        if overlap >= chunk_size:
            raise ValueError("chunk overlap must be less than chunk size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def build_chunks(self, paragraphs: list[ParagraphBlock]) -> list[ChunkDraft]:
        if not paragraphs:
            return []

        chunks: list[ChunkDraft] = []
        chunk_index = 0

        buffer_text = ""
        buffer_path = ""
        buffer_type = "paragraph"

        def flush_buffer() -> None:
            nonlocal chunk_index, buffer_text
            if not buffer_text:
                return
            chunks.append(
                self._make_chunk(
                    chunk_index=chunk_index,
                    section_path=buffer_path,
                    text=buffer_text,
                    content_type=buffer_type,
                )
            )
            chunk_index += 1
            buffer_text = ""

        for block in paragraphs:
            text = block.text.strip()
            if not text:
                continue

            if not buffer_text:
                buffer_text = text
                buffer_path = block.section_path
                buffer_type = block.content_type
                continue

            # Keep chunks within section boundaries to reduce semantic noise.
            if block.section_path != buffer_path or block.content_type != buffer_type:
                flush_buffer()
                buffer_text = text
                buffer_path = block.section_path
                buffer_type = block.content_type
                continue

            candidate = f"{buffer_text}\n{text}"
            if len(candidate) <= self.chunk_size:
                buffer_text = candidate
                continue

            previous_buffer = buffer_text
            flush_buffer()

            tail = previous_buffer[-self.overlap :] if self.overlap > 0 else ""
            buffer_text = f"{tail}\n{text}" if tail else text
            buffer_path = block.section_path
            buffer_type = block.content_type

        flush_buffer()

        return chunks

    def _make_chunk(self, *, chunk_index: int, section_path: str, text: str, content_type: str) -> ChunkDraft:
        token_count = len(_TOKEN_RE.findall(text))
        return ChunkDraft(
            chunk_index=chunk_index,
            section_path=section_path,
            chunk_text=text,
            token_count=token_count,
            content_type=content_type,
            pedagogical_role=_infer_role(text),
        )
