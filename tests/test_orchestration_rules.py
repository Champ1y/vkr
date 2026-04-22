from __future__ import annotations

from app.services.orchestration import AskOrchestrationService


def test_resolve_corpora_answer_mode() -> None:
    assert AskOrchestrationService.resolve_corpora("answer", False) == ["official"]


def test_resolve_corpora_tutorial_without_extended() -> None:
    assert AskOrchestrationService.resolve_corpora("tutorial", False) == ["official"]


def test_resolve_corpora_tutorial_with_extended() -> None:
    assert AskOrchestrationService.resolve_corpora("tutorial", True) == ["official", "supplementary"]
