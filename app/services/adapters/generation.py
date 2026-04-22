from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.ask import TutorialPayload
from app.services.query_processing import analyze_query
from app.services.types import RankedChunk

logger = get_logger(__name__)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_SOURCE_BLOCK_RE = re.compile(r"\n+\s*(источники|sources)\s*:.*", flags=re.IGNORECASE | re.DOTALL)
_SOURCE_PHRASE_RE = re.compile(r"\n+\s*ниже приведены ссылки на источники\s*:.*", flags=re.IGNORECASE | re.DOTALL)
_SOURCE_GENERIC_RE = re.compile(r"\n+\s*ниже\s+.*источ[а-яa-z]*\s*:.*", flags=re.IGNORECASE | re.DOTALL)


def _clip(text: str, limit: int = 320) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _build_context(*, question: str, mode: str, ranked_chunks: list[RankedChunk], max_items: int) -> str:
    analysis = analyze_query(question)

    def mode_priority(item: RankedChunk) -> float:
        bonus = 0.0
        role = item.pedagogical_role
        lowered_path = f"{item.title} {item.section_path}".lower()

        if mode == "tutorial":
            if analysis.intent == "procedural":
                if role == "step":
                    bonus += 0.18
                elif role == "prerequisite":
                    bonus += 0.14
                elif role == "example":
                    bonus += 0.10
            if "configuration" in lowered_path or "quick setup" in lowered_path or "sql-" in lowered_path:
                bonus += 0.07
        else:
            if role in {"overview", "warning"}:
                bonus += 0.08
            if any(marker in lowered_path for marker in ("overview", "concept", "restrictions", "compatibility")):
                bonus += 0.06
            if analysis.intent == "compatibility":
                if any(marker in lowered_path for marker in ("restriction", "compatibility", "major version", "publisher", "subscriber")):
                    bonus += 0.22
                else:
                    bonus -= 0.05

        if analysis.is_logical_replication and any(
            marker in lowered_path for marker in ("logical replication", "publication", "subscription")
        ):
            bonus += 0.10

        return item.score + bonus

    sorted_items = sorted(ranked_chunks, key=mode_priority, reverse=True)

    selected: list[RankedChunk] = []
    fingerprints: set[str] = set()
    per_doc_counter: dict[str, int] = {}

    for item in sorted_items:
        normalized_chunk = " ".join(item.chunk_text.lower().split())
        fingerprint = normalized_chunk[:220]
        if fingerprint in fingerprints:
            continue

        doc_key = f"{item.source_url}::{item.section_path}"
        if per_doc_counter.get(doc_key, 0) >= 2:
            continue

        selected.append(item)
        fingerprints.add(fingerprint)
        per_doc_counter[doc_key] = per_doc_counter.get(doc_key, 0) + 1
        if len(selected) >= max_items:
            break

    lines: list[str] = []
    for idx, item in enumerate(selected, start=1):
        lines.append(
            f"[{idx}] corpus={item.corpus_type}; rank={item.rank_position}; score={item.score:.4f}; "
            f"title={item.title}; section={item.section_path}; url={item.source_url}"
        )
        lines.append(f"[{idx}] text={_clip(item.chunk_text, 1100)}")

    return "\n".join(lines)


def _sanitize_answer_text(content: str, *, max_sentences: int = 6) -> str:
    text = content.strip()
    text = _SOURCE_PHRASE_RE.sub("", text)
    text = _SOURCE_BLOCK_RE.sub("", text)
    text = _SOURCE_GENERIC_RE.sub("", text)

    sentences = [chunk.strip() for chunk in _SENTENCE_SPLIT_RE.split(text) if chunk.strip()]
    if len(sentences) > max_sentences:
        text = " ".join(sentences[:max_sentences]).strip()
    return text


def _stabilize_tutorial_payload(*, question: str, payload: TutorialPayload, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
    q_lower = question.lower()
    context = "\n".join(
        f"{item.title}\n{item.section_path}\n{item.chunk_text}".lower()
        for item in ranked_chunks
    )

    looks_like_add_table_flow = ("добав" in q_lower and "табл" in q_lower) or ("add" in q_lower and "table" in q_lower)
    logical_topic = "logical replication" in q_lower or "логическ" in q_lower

    if looks_like_add_table_flow and logical_topic:
        has_alter_publication = "alter publication" in context
        has_refresh_publication = "refresh publication" in context or "alter subscription" in context
        steps = list(payload.steps)

        if has_alter_publication and not any("alter publication" in step.lower() for step in steps):
            steps.insert(0, "На publisher выполните: ALTER PUBLICATION <publication_name> ADD TABLE <schema.table>;")
        if has_refresh_publication and not any("refresh publication" in step.lower() for step in steps):
            steps.append("На subscriber выполните: ALTER SUBSCRIPTION <subscription_name> REFRESH PUBLICATION;")

        prerequisites = list(payload.prerequisites)
        if has_alter_publication and not any("publication" in item.lower() for item in prerequisites):
            prerequisites.append("Должна существовать publication, в которую добавляется таблица.")
        if has_refresh_publication and not any("subscription" in item.lower() for item in prerequisites):
            prerequisites.append("Должна существовать subscription, которую нужно обновить.")

        return TutorialPayload(
            short_explanation=payload.short_explanation,
            prerequisites=prerequisites,
            steps=steps,
            notes=payload.notes,
        )

    return payload


_ANSWER_SYSTEM = (
    "Ты — помощник по документации PostgreSQL. Отвечай только на русском языке. "
    "Используй только предоставленный контекст. Не выдумывай факты. "
    "Если данных недостаточно — прямо скажи об этом. "
    "Не смешивай версии PostgreSQL. Учитывай только выбранную major-версию. "
    "Не додумывай команды, параметры и шаги, которых нет в контексте. "
    "Не подменяй logical replication механизмами LISTEN/NOTIFY, pg_receivewal, pg_basebackup "
    "или physical replication, если это не подтверждено контекстом. "
    "Дай краткий проверяемый ответ (2-6 предложений). "
    "Не добавляй список источников в основной текст ответа, источники возвращаются отдельно."
)

_TUTORIAL_SYSTEM = (
    "Ты — помощник по документации PostgreSQL для начинающих. "
    "Отвечай только на русском языке. "
    "Используй только предоставленный контекст, без выдуманных фактов. "
    "Если данных недостаточно — честно сообщи об этом. "
    "Не смешивай версии PostgreSQL. "
    "Если вопрос процедурный, дай пошаговое руководство только по подтвержденным данным. "
    "Не добавляй шаги, команды или параметры, если их нет в контексте. "
    "Не подменяй logical replication механизмами LISTEN/NOTIFY, pg_receivewal, pg_basebackup "
    "или physical replication, если это не подтверждено контекстом. "
    "Если данных не хватает, верни пустой список steps и объясни ограничение в notes. "
    "Верни строго валидный JSON с ключами: short_explanation, prerequisites, steps, notes. "
    "short_explanation — строка; prerequisites/steps/notes — массивы строк. "
    "Не добавляй список источников в JSON, источники возвращаются отдельно."
)


class BaseGenerationService(ABC):
    @abstractmethod
    def generate_answer(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_tutorial(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
        raise NotImplementedError


class GroqGenerationService(BaseGenerationService):
    def __init__(self) -> None:
        self.api_key = settings.groq_api_key.strip()
        self.model_name = settings.groq_model.strip()
        self.base_url = settings.groq_base_url.rstrip("/")
        self._client: OpenAI | None = None

    def _ensure_client(self) -> OpenAI:
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY не задан. Заполните .env: GROQ_API_KEY=<ваш_ключ>, "
                "затем пересоздайте backend: docker compose up -d --force-recreate backend"
            )
        if not self.model_name:
            raise RuntimeError(
                "GROQ_MODEL не задан. Заполните .env, например: GROQ_MODEL=llama-3.1-8b-instant, "
                "затем перезапустите backend."
            )
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def _chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        client = self._ensure_client()
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                temperature=temperature,
                messages=messages,
            )
        except AuthenticationError as exc:
            raise RuntimeError("Ошибка аутентификации Groq: проверьте GROQ_API_KEY.") from exc
        except APIConnectionError as exc:
            raise RuntimeError(f"Groq API недоступен ({self.base_url}). Проверьте сеть и доступность сервиса.") from exc
        except APIStatusError as exc:
            if exc.status_code == 404:
                raise RuntimeError(
                    f"Модель '{self.model_name}' не найдена или не поддерживается в Groq. "
                    "Проверьте GROQ_MODEL."
                ) from exc
            if exc.status_code in {401, 403}:
                raise RuntimeError("Groq отклонил запрос: проверьте GROQ_API_KEY и права доступа.") from exc
            raise RuntimeError(f"Ошибка Groq API (HTTP {exc.status_code}).") from exc

        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise RuntimeError("Groq API вернул пустой ответ.")
        return content

    def generate_answer(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> str:
        analysis = analyze_query(question)
        context = _build_context(question=question, mode="answer", ranked_chunks=ranked_chunks, max_items=7)
        extra_instruction = ""
        if analysis.intent == "compatibility":
            extra_instruction = (
                "Проверь фразы о compatibility/restrictions/major version между publisher и subscriber. "
                "Если такие фразы есть, обязательно перескажи их по-русски и не отвечай 'нет информации'. "
            )
        prompt = (
            f"Вопрос: {question}\n"
            f"Версия PostgreSQL: {pg_version}\n"
            f"Контекст:\n{context}\n\n"
            f"{extra_instruction}"
            "Сформируй краткий проверяемый ответ по контексту. "
            "Если подтверждения недостаточно, так и напиши без домыслов."
        )
        raw = self._chat(
            messages=[
                {"role": "system", "content": _ANSWER_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return _sanitize_answer_text(raw)

    def generate_tutorial(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
        context = _build_context(question=question, mode="tutorial", ranked_chunks=ranked_chunks, max_items=10)
        prompt = (
            f"Вопрос: {question}\n"
            f"Версия PostgreSQL: {pg_version}\n"
            f"Контекст:\n{context}\n\n"
            "Верни только JSON с ключами short_explanation, prerequisites, steps, notes. "
            "Каждый пункт steps и prerequisites должен быть подтвержден контекстом."
        )
        content = self._chat(
            messages=[
                {"role": "system", "content": _TUTORIAL_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        payload = _parse_tutorial_json(content)
        return _stabilize_tutorial_payload(question=question, payload=payload, ranked_chunks=ranked_chunks)


class GenerationService(BaseGenerationService):
    """Groq-only generation service (OpenAI-compatible API)."""

    def __init__(self) -> None:
        self._groq = GroqGenerationService()
        logger.info(
            "Using Groq generation base_url=%s model=%s",
            settings.groq_base_url,
            settings.groq_model or "<unset>",
        )

    def generate_answer(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> str:
        return self._groq.generate_answer(question=question, pg_version=pg_version, ranked_chunks=ranked_chunks)

    def generate_tutorial(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
        return self._groq.generate_tutorial(question=question, pg_version=pg_version, ranked_chunks=ranked_chunks)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _parse_tutorial_json(content: str) -> TutorialPayload:
    """Extract TutorialPayload from LLM response that may contain extra text around JSON."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise
        payload = json.loads(content[start: end + 1])

    def _strings(key: str) -> list[str]:
        return [str(x).strip() for x in payload.get(key, []) if str(x).strip()]

    return TutorialPayload(
        short_explanation=str(payload.get("short_explanation", "")).strip(),
        prerequisites=_strings("prerequisites"),
        steps=_strings("steps"),
        notes=_strings("notes"),
    )
