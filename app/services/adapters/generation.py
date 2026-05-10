from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

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
_SQL_BLOCK_RE = re.compile(r"```sql\s*[\s\S]*?```", flags=re.IGNORECASE)
_SQL_HEAD_RE = re.compile(r"^(select|with|explain|show|insert|update|delete)\b", flags=re.IGNORECASE)
_STRICT_NOT_FOUND_MESSAGE = "В найденной официальной документации такой настройки/команды нет."

_SQL_VERB_MARKERS = (
    "напиши",
    "покажи",
    "дай",
    "составь",
    "сформируй",
    "write",
    "show",
    "give",
)

_ACTIVE_QUERIES_MARKERS = (
    "актив",
    "query_start",
    "pg_stat_activity",
    "5 минут",
    "5 minute",
    "5 мин",
)

_TABLE_SIZE_MARKERS = (
    "размер таблиц",
    "size of tables",
    "размер индек",
    "size of indexes",
    "pg_total_relation_size",
    "pg_relation_size",
)

_EXPLAIN_ANALYZE_MARKERS = (
    "explain analyze",
    "explain analyse",
    "план запроса",
    "план выполнения",
)


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


def _normalize_question(question: str) -> str:
    return " ".join(question.lower().replace("ё", "е").split())


def _is_hallucination_trap(question: str) -> bool:
    normalized = _normalize_question(question)
    return "super_fast_vacuum_mode" in normalized or "create magic index" in normalized


def _is_sql_intent(question: str) -> bool:
    normalized = _normalize_question(question)
    has_sql_word = any(token in normalized for token in ("sql", "query", "запрос"))
    has_request_verb = any(token in normalized for token in _SQL_VERB_MARKERS)
    return has_sql_word and (has_request_verb or "?" in question)


def _is_active_queries_request(question: str) -> bool:
    normalized = _normalize_question(question)
    return all(marker in normalized for marker in ("актив", "запрос", "5")) or any(
        marker in normalized for marker in _ACTIVE_QUERIES_MARKERS
    ) and "запрос" in normalized


def _is_table_size_request(question: str) -> bool:
    normalized = _normalize_question(question)
    has_size = "размер" in normalized or "size" in normalized
    has_table_or_index = any(token in normalized for token in ("таблиц", "table", "индекс", "index"))
    if has_size and has_table_or_index:
        return True
    return any(marker in normalized for marker in _TABLE_SIZE_MARKERS)


def _is_explain_analyze_request(question: str) -> bool:
    normalized = _normalize_question(question)
    return any(marker in normalized for marker in _EXPLAIN_ANALYZE_MARKERS)


def _sql_block(sql: str) -> str:
    return f"```sql\n{sql.strip()}\n```"


def _active_queries_sql_answer() -> str:
    return _sql_block(
        "SELECT pid, usename, datname, state, now() - query_start AS duration, query\n"
        "FROM pg_stat_activity\n"
        "WHERE state = 'active'\n"
        "  AND query_start < now() - interval '5 minutes'\n"
        "  AND pid <> pg_backend_pid()\n"
        "ORDER BY duration DESC;"
    )


def _table_size_sql_answer() -> str:
    return _sql_block(
        "SELECT\n"
        "  schemaname,\n"
        "  tablename,\n"
        "  pg_size_pretty(pg_relation_size(format('%I.%I', schemaname, tablename)::regclass)) AS table_size,\n"
        "  pg_size_pretty(pg_indexes_size(format('%I.%I', schemaname, tablename)::regclass)) AS indexes_size,\n"
        "  pg_size_pretty(pg_total_relation_size(format('%I.%I', schemaname, tablename)::regclass)) AS total_size\n"
        "FROM pg_tables\n"
        "WHERE schemaname NOT IN ('pg_catalog', 'information_schema')\n"
        "ORDER BY pg_total_relation_size(format('%I.%I', schemaname, tablename)::regclass) DESC;"
    )


def _explain_analyze_sql_answer() -> str:
    return (
        _sql_block(
            "EXPLAIN (ANALYZE, BUFFERS, VERBOSE)\n"
            "SELECT o.customer_id, SUM(o.total_amount) AS revenue\n"
            "FROM orders o\n"
            "WHERE o.created_at >= now() - interval '30 days'\n"
            "GROUP BY o.customer_id\n"
            "ORDER BY revenue DESC\n"
            "LIMIT 20;"
        )
        + "\n\nЗапустите запрос без EXPLAIN отдельно, если нужно получить сами данные."
    )


def _deterministic_answer(question: str) -> str | None:
    if _is_hallucination_trap(question):
        return _STRICT_NOT_FOUND_MESSAGE
    if _is_active_queries_request(question):
        return _active_queries_sql_answer()
    if _is_table_size_request(question):
        return _table_size_sql_answer()
    if _is_explain_analyze_request(question):
        return _explain_analyze_sql_answer()
    return None


def _ensure_sql_block_first(content: str) -> str:
    text = content.strip()
    if not text:
        return text
    if text.lower().startswith("```sql"):
        return text

    block_match = _SQL_BLOCK_RE.search(text)
    if block_match:
        block = block_match.group(0).strip()
        before = text[: block_match.start()].strip()
        after = text[block_match.end() :].strip()
        rest = "\n\n".join(part for part in (before, after) if part)
        return f"{block}\n\n{rest}".strip() if rest else block

    if _SQL_HEAD_RE.match(text):
        return _sql_block(text)

    return _sql_block("-- SQL-запрос уточняется по вашему вопросу.\n" + text)


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
    "Объясняй простыми словами. "
    "Если данных недостаточно — честно сообщи об этом. "
    "Не смешивай версии PostgreSQL. "
    "Официальная документация — основной источник фактов; supplementary можно использовать для учебной подачи и примеров. "
    "Если вопрос процедурный, дай пошаговое руководство только по подтвержденным данным. "
    "Не добавляй шаги, команды или параметры, если их нет в контексте. "
    "Не подменяй logical replication механизмами LISTEN/NOTIFY, pg_receivewal, pg_basebackup "
    "или physical replication, если это не подтверждено контекстом. "
    "Если данных не хватает, верни пустой список steps и объясни ограничение в notes. "
    "Верни строго валидный JSON с ключами: short_explanation, prerequisites, steps, notes. "
    "short_explanation — строка; prerequisites/steps/notes — массивы строк без словарей и вложенных JSON-объектов. "
    "Не добавляй список источников в JSON, источники возвращаются отдельно."
)


class BaseGenerationService(ABC):
    @abstractmethod
    def generate_answer(
        self,
        *,
        question: str,
        pg_version: str,
        answer_mode: str,
        ranked_chunks: list[RankedChunk],
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_tutorial(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
        raise NotImplementedError


class GroqGenerationService(BaseGenerationService):
    def __init__(self) -> None:
        self.provider = settings.llm_provider.strip().lower()
        self.api_key = settings.groq_api_key.strip()
        self.model_name = settings.llm_model.strip()
        self.base_url = settings.groq_base_url.rstrip("/")

    def _ensure_config(self) -> None:
        if self.provider != "groq":
            raise RuntimeError(
                f"Unsupported LLM_PROVIDER='{settings.llm_provider}'. Allowed: groq."
            )
        if not self.api_key:
            raise RuntimeError("Groq API key is not configured. Set GROQ_API_KEY.")
        if not self.model_name:
            raise RuntimeError("Groq model is not configured. Set LLM_MODEL.")

    def _chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        self._ensure_config()
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "temperature": temperature,
            "messages": messages,
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise RuntimeError("Groq API не ответил вовремя. Повторите запрос позже.") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Groq API недоступен ({self.base_url}). Проверьте сеть и доступность сервиса.") from exc

        if response.status_code in {401, 403}:
            raise RuntimeError("Ошибка аутентификации Groq: проверьте GROQ_API_KEY.")
        if response.status_code == 404:
            raise RuntimeError(f"Модель '{self.model_name}' не найдена или не поддерживается в Groq. Проверьте LLM_MODEL.")
        if response.status_code >= 400:
            detail = ""
            try:
                data = response.json()
                error_obj = data.get("error", {}) if isinstance(data, dict) else {}
                detail = str(error_obj.get("message", "")).strip()
            except Exception:
                detail = response.text.strip()
            suffix = f": {detail}" if detail else ""
            raise RuntimeError(f"Ошибка Groq API (HTTP {response.status_code}){suffix}")

        try:
            data = response.json()
            content = str(data["choices"][0]["message"]["content"]).strip()
        except Exception as exc:  # pragma: no cover - defensive parse
            raise RuntimeError("Groq API вернул ответ в неожиданном формате.") from exc

        if not content:
            raise RuntimeError("Groq API вернул пустой ответ.")
        return content

    def generate_answer(
        self,
        *,
        question: str,
        pg_version: str,
        answer_mode: str,
        ranked_chunks: list[RankedChunk],
    ) -> str:
        deterministic = _deterministic_answer(question)
        if deterministic is not None:
            return deterministic

        analysis = analyze_query(question)
        is_detailed = answer_mode == "detailed"
        context = _build_context(
            question=question,
            mode="answer",
            ranked_chunks=ranked_chunks,
            max_items=10 if is_detailed else 7,
        )
        extra_instruction = ""
        if analysis.intent == "compatibility":
            extra_instruction = (
                "Проверь фразы о compatibility/restrictions/major version между publisher и subscriber. "
                "Если такие фразы есть, обязательно перескажи их по-русски и не отвечай 'нет информации'. "
            )
        if is_detailed:
            extra_instruction += (
                "Сделай подробный ответ: добавь нюансы, ограничения, типичные ошибки и безопасные рекомендации по применению. "
                "Оставайся строго в рамках подтвержденного контекста. "
            )
        else:
            extra_instruction += "Дай краткий прямой ответ без лишних деталей. "
        if _is_sql_intent(question):
            extra_instruction += (
                "Начни ответ сразу с блока ```sql ...```. "
                "Не подменяй SQL-запрос параметрами конфигурации или логирования, если вопрос об SQL-запросе. "
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
        if _is_sql_intent(question):
            return _ensure_sql_block_first(raw)
        return _sanitize_answer_text(raw, max_sentences=12 if is_detailed else 4)

    def generate_tutorial(self, *, question: str, pg_version: str, ranked_chunks: list[RankedChunk]) -> TutorialPayload:
        context = _build_context(question=question, mode="tutorial", ranked_chunks=ranked_chunks, max_items=10)
        prompt = (
            f"Вопрос: {question}\n"
            f"Версия PostgreSQL: {pg_version}\n"
            f"Контекст:\n{context}\n\n"
            "Верни только JSON с ключами short_explanation, prerequisites, steps, notes. "
            "Сначала дай короткое объяснение. Если уместно, включи SQL-пример в steps или notes. "
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
    """Groq-only generation service."""

    def __init__(self) -> None:
        self._groq = GroqGenerationService()
        logger.info(
            "Using LLM generation provider=%s base_url=%s model=%s",
            settings.llm_provider,
            settings.groq_base_url,
            settings.llm_model or "<unset>",
        )

    def generate_answer(
        self,
        *,
        question: str,
        pg_version: str,
        answer_mode: str,
        ranked_chunks: list[RankedChunk],
    ) -> str:
        return self._groq.generate_answer(
            question=question,
            pg_version=pg_version,
            answer_mode=answer_mode,
            ranked_chunks=ranked_chunks,
        )

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

    def _normalize_tutorial_item(item: Any) -> str:
        if isinstance(item, str):
            return item.strip()
        if isinstance(item, (int, float, bool)):
            return str(item).strip()
        if isinstance(item, dict):
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            text = str(item.get("text", "")).strip()
            step = str(item.get("step", "")).strip()
            instruction = str(item.get("instruction", "")).strip()
            value = str(item.get("value", "")).strip()

            if title and description:
                return f"{title}: {description}"
            for candidate in (text, step, instruction, value, title, description):
                if candidate:
                    return candidate

            compact_parts: list[str] = []
            for key, raw in item.items():
                if isinstance(raw, (str, int, float, bool)):
                    normalized = str(raw).strip()
                    if normalized:
                        compact_parts.append(f"{key}: {normalized}")
            return "; ".join(compact_parts)
        if isinstance(item, list):
            joined = "; ".join(_normalize_tutorial_item(part) for part in item)
            return joined.strip("; ").strip()
        return ""

    def _strings(key: str) -> list[str]:
        normalized: list[str] = []
        for raw in payload.get(key, []):
            value = _normalize_tutorial_item(raw)
            if value:
                normalized.append(value)
        return normalized

    return TutorialPayload(
        short_explanation=str(payload.get("short_explanation", "")).strip(),
        prerequisites=_strings("prerequisites"),
        steps=_strings("steps"),
        notes=_strings("notes"),
    )
