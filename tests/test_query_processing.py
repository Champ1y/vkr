from __future__ import annotations

from app.services.query_processing import analyze_query


def test_russian_logical_replication_query_expands_english_terms() -> None:
    analysis = analyze_query("Какие параметры нужны для логической репликации в PostgreSQL 16?")

    assert analysis.is_logical_replication is True
    assert "logical replication" in analysis.expanded_terms
    assert "publication" in analysis.expanded_terms
    assert "subscription" in analysis.expanded_terms
    assert "wal_level" in analysis.expanded_terms


def test_procedural_intent_detected() -> None:
    analysis = analyze_query("Как добавить таблицу в существующую publication и обновить subscription?")
    assert analysis.intent == "procedural"


def test_comparative_query_adds_release_hints() -> None:
    analysis = analyze_query("Что нового в logical replication в PostgreSQL 17 по сравнению с 16?")
    assert analysis.intent == "comparative"
    assert "release notes" in analysis.expanded_terms


def test_parameter_focus_detected_for_replication_settings_query() -> None:
    analysis = analyze_query("Какие параметры проверить для logical replication?")
    assert analysis.parameter_focus is True
    assert "runtime-config-replication" in analysis.expanded_terms


def test_compatibility_intent_detected_and_adds_restriction_terms() -> None:
    analysis = analyze_query("Можно ли использовать logical replication между разными major-версиями PostgreSQL?")
    assert analysis.intent == "compatibility"
    assert "logical-replication-restrictions" in analysis.expanded_terms
