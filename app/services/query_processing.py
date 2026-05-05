from __future__ import annotations

import re
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-я0-9_]+")

_PROCEDURAL_MARKERS = {
    "как",
    "how",
    "шаг",
    "steps",
    "step",
    "настро",
    "configure",
    "enable",
    "включ",
    "добав",
    "add",
}
_COMPARATIVE_MARKERS = {
    "что нового",
    "изменил",
    "нововвед",
    "difference",
    "compared",
    "compared to",
    "vs",
}
_DEFINITION_MARKERS = {
    "что такое",
    "what is",
    "объясни",
    "explain",
    "meaning",
}
_COMPATIBILITY_MARKERS = {
    "different major",
    "cross-version",
    "major version",
    "между разными major",
    "между разными версиями",
    "совместим",
    "compatibility",
}

_TERM_VARIANTS: dict[str, set[str]] = {
    "logical replication": {
        "logical replication",
        "logical-replication",
        "логическая репликация",
        "логической репликации",
        "логическую репликацию",
    },
    "publication": {
        "publication",
        "publications",
        "публикация",
        "публикации",
        "alter publication",
        "create publication",
    },
    "subscription": {
        "subscription",
        "subscriptions",
        "подписка",
        "подписки",
        "alter subscription",
        "create subscription",
    },
    "standby": {
        "standby",
        "standby server",
        "hot standby",
        "реплика",
        "реплике",
        "реплику",
        "резерв",
    },
    "replication slot": {
        "replication slot",
        "replication slots",
        "слот репликации",
        "слоты репликации",
    },
    "wal_level": {"wal_level", "wal level"},
    "max_replication_slots": {"max_replication_slots"},
    "max_wal_senders": {"max_wal_senders"},
    "pg_createsubscriber": {"pg_createsubscriber"},
    "alter publication": {"alter publication", "add table"},
    "refresh publication": {"refresh publication", "alter subscription refresh publication"},
}

_LOGICAL_DISTRACTOR_TERMS = {
    "listen",
    "notify",
    "pg_receivewal",
    "pg_receivexlog",
    "pg_basebackup",
    "physical replication",
    "streaming replication",
}


@dataclass(slots=True)
class QueryAnalysis:
    raw_question: str
    normalized_question: str
    embedding_query: str
    tokens: set[str]
    technical_terms: set[str]
    expanded_terms: list[str]
    intent: str
    is_logical_replication: bool
    parameter_focus: bool


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text)}


def normalize_question(text: str) -> str:
    return " ".join(text.lower().replace("ё", "е").split())


def _contains_phrase(haystack: str, phrase: str) -> bool:
    if not phrase:
        return False
    return phrase in haystack


def _detect_intent(normalized: str) -> str:
    if any(marker in normalized for marker in _COMPATIBILITY_MARKERS):
        return "compatibility"
    if any(marker in normalized for marker in _COMPARATIVE_MARKERS):
        return "comparative"
    if any(marker in normalized for marker in _PROCEDURAL_MARKERS):
        return "procedural"
    if any(marker in normalized for marker in _DEFINITION_MARKERS):
        return "definition"
    return "factual"


def analyze_query(question: str) -> QueryAnalysis:
    normalized = normalize_question(question)
    tokens = tokenize(normalized)
    intent = _detect_intent(normalized)

    detected_terms: set[str] = set()
    expanded_terms: list[str] = []

    for canonical, variants in _TERM_VARIANTS.items():
        variants_normalized = {normalize_question(v) for v in variants}
        matched = False
        if canonical in tokens:
            matched = True
        if not matched:
            matched = any(_contains_phrase(normalized, variant) for variant in variants_normalized)
        if matched:
            detected_terms.add(canonical)
            for variant in sorted(variants_normalized):
                if variant and variant not in expanded_terms:
                    expanded_terms.append(variant)

    has_logical_phrase = "logical replication" in normalized or "логическ" in normalized and "репликац" in normalized
    is_logical_replication = has_logical_phrase or "logical replication" in detected_terms
    parameter_focus = any(marker in normalized for marker in ("парамет", "parameter", "setting", "настройк", "config"))

    if is_logical_replication:
        for term in [
            "logical replication",
            "publication",
            "subscription",
            "replication slot",
            "wal_level",
            "max_replication_slots",
            "max_wal_senders",
        ]:
            if term not in detected_terms:
                detected_terms.add(term)
            if term not in expanded_terms:
                expanded_terms.append(term)
        if intent == "procedural":
            for term in [
                "alter publication",
                "add table",
                "alter subscription",
                "refresh publication",
                "sql-alterpublication",
                "sql-altersubscription",
            ]:
                if term not in detected_terms:
                    detected_terms.add(term)
                if term not in expanded_terms:
                    expanded_terms.append(term)
        if parameter_focus:
            for term in ["configuration settings", "runtime-config-replication"]:
                if term not in expanded_terms:
                    expanded_terms.append(term)

    if intent == "comparative":
        for term in ["release notes", "what's new", "release"]:
            if term not in expanded_terms:
                expanded_terms.append(term)
    if intent == "compatibility":
        for term in [
            "compatibility",
            "restrictions",
            "major version",
            "logical-replication-restrictions",
            "publisher",
            "subscriber",
        ]:
            if term not in expanded_terms:
                expanded_terms.append(term)

    # Add token-level hints for phrase terms to improve lexical matching in SQL.
    for term in list(expanded_terms):
        for token in sorted(tokenize(term)):
            if len(token) >= 4 and token not in expanded_terms:
                expanded_terms.append(token)

    def term_priority(term: str) -> tuple[int, int, str]:
        priority = 0
        if term in detected_terms:
            priority += 5
        if term in {
            "logical replication",
            "publication",
            "subscription",
            "replication slot",
            "wal_level",
            "max_replication_slots",
            "max_wal_senders",
            "alter publication",
            "alter subscription",
            "refresh publication",
            "add table",
            "sql-alterpublication",
            "sql-altersubscription",
            "runtime-config-replication",
            "release notes",
        }:
            priority += 6
        if any(ch in term for ch in ("_", "-", "sql-")):
            priority += 2
        if re.search(r"[a-z]", term):
            priority += 1
        if re.search(r"[а-я]", term):
            priority -= 1
        return priority, len(term), term

    # Keep keyword list compact and deterministic for SQL lexical search.
    unique_terms = [term for term in dict.fromkeys(expanded_terms) if len(term) >= 3]
    compact_terms = sorted(unique_terms, key=term_priority, reverse=True)[:16]
    embedding_query = question.strip()
    if compact_terms:
        embedding_query += "\n\nTechnical search hints (EN): " + "; ".join(compact_terms)

    return QueryAnalysis(
        raw_question=question,
        normalized_question=normalized,
        embedding_query=embedding_query,
        tokens=tokens,
        technical_terms=detected_terms,
        expanded_terms=compact_terms,
        intent=intent,
        is_logical_replication=is_logical_replication,
        parameter_focus=parameter_focus,
    )


def overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left:
        return 0.0
    return len(left & right) / max(len(left), 1)


def technical_term_overlap(text: str, technical_terms: set[str]) -> float:
    if not technical_terms:
        return 0.0
    haystack = normalize_question(text)
    matched = 0
    for canonical in technical_terms:
        variants = _TERM_VARIANTS.get(canonical, {canonical})
        if any(normalize_question(variant) in haystack for variant in variants):
            matched += 1
    return matched / max(len(technical_terms), 1)


def logical_confusion_penalty(*, text: str, analysis: QueryAnalysis) -> float:
    if not analysis.is_logical_replication:
        return 0.0
    haystack = normalize_question(text)
    has_anchor = "logical replication" in haystack or ("publication" in haystack and "subscription" in haystack)
    has_distractor = any(term in haystack for term in _LOGICAL_DISTRACTOR_TERMS)
    if has_distractor and not has_anchor:
        return 0.22
    return 0.0
