from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_TEMPLATE = PROJECT_ROOT / "app" / "web" / "templates" / "index.html"
HISTORY_TEMPLATE = PROJECT_ROOT / "app" / "web" / "templates" / "history.html"
APP_JS = PROJECT_ROOT / "app" / "web" / "static" / "app.js"
HISTORY_JS = PROJECT_ROOT / "app" / "web" / "static" / "history.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_main_screen_has_no_removed_blocks() -> None:
    html = _read(INDEX_TEMPLATE)
    js = _read(APP_JS)

    removed = [
        "Состояние " + "корпуса",
        "Логика " + "режимов",
        "Расширенный " + "учебный режим",
        "Расширенный " + "режим включён",
    ]

    for phrase in removed:
        assert phrase not in html
        assert phrase not in js


def test_main_screen_has_user_focused_blocks() -> None:
    html = _read(INDEX_TEMPLATE)

    assert "Примеры вопросов" in html
    assert "Недавние запросы" in html
    assert "Источники" in html
    assert "inline-examples" not in html
    assert "quick-chips" not in html
    assert "О системе" not in html


def test_hero_has_no_technical_badges() -> None:
    html = _read(INDEX_TEMPLATE)

    assert 'class="status-chips"' not in html
    assert "Official Docs" not in html
    assert "Tutorial Mode" not in html
    assert "BAAI/bge-m3" not in html


def test_unified_assistant_panel_structure_exists() -> None:
    html = _read(INDEX_TEMPLATE)

    assert 'class="card assistant-panel"' in html
    assert 'id="answer-zone" class="answer-zone"' in html
    assert 'id="sources-zone" class="sources-zone"' in html


def test_main_screen_has_only_three_answer_modes() -> None:
    html = _read(INDEX_TEMPLATE)

    assert "Краткий" in html
    assert "Подробный" in html
    assert "Обучающий" in html

    assert 'id="mode-short" value="short"' in html
    assert 'id="mode-detailed" value="detailed"' in html
    assert 'id="mode-tutorial" value="tutorial"' in html


def test_frontend_payload_uses_only_question_pg_version_answer_mode() -> None:
    js = _read(APP_JS)

    assert "question," in js
    assert "pg_version:" in js
    assert "answer_mode: selectedAnswerMode()" in js

    assert ("extended" + "_tutorial") not in js
    assert ("use" + "_supplementary") not in js
    assert ("include" + "_supplementary") not in js


def test_clarification_ui_is_removed() -> None:
    html = _read(INDEX_TEMPLATE)
    js = _read(APP_JS)

    assert "clarification-panel" not in html
    assert "Нужно уточнение" not in html
    assert "clarification" not in js


def test_about_block_removed() -> None:
    html = _read(INDEX_TEMPLATE)
    js = _read(APP_JS)

    assert "about-details" not in html
    assert "about-system" not in html
    assert "open-about-btn" not in html
    assert "open-about-btn" not in js


def test_sources_show_more_hidden_when_no_sources() -> None:
    js = _read(APP_JS)
    html = _read(INDEX_TEMPLATE)

    assert 'id="sources-more-btn"' in html
    assert "sourcesMoreBtn.hidden = true;" in js
    assert 'clearSourcesUI("Источники появятся после ответа.")' in js


def test_empty_sections_are_hidden_not_rendered() -> None:
    js = _read(APP_JS)

    assert "function isEmptySection(value)" in js
    assert "sectionEl.hidden = empty;" in js
    assert "tutorialSummarySection.hidden = isEmptySection(summary);" in js


def test_sql_block_has_copy_button() -> None:
    js = _read(APP_JS)

    assert "function renderSQLBlock(sqlRaw, language = \"SQL\")" in js
    assert 'copyBtn.className = "copy-sql-btn";' in js
    assert 'copyBtn.textContent = "Копировать";' in js


def test_error_shows_collapsed_technical_details() -> None:
    html = _read(INDEX_TEMPLATE)
    js = _read(APP_JS)

    assert '<details class="alert-details">' in html
    assert "Технические детали" in html
    assert "error-technical" in html

    assert "function showGlobalError(message, details = \"\")" in js
    assert "errorDetails.textContent" in js


def test_sidebar_history_is_limited_to_four() -> None:
    js = _read(APP_JS)

    assert "fetch(\"/api/history?limit=4\")" in js
    assert "items.slice(0, 4)" in js


def test_history_page_uses_neutral_completion_status() -> None:
    history_html = _read(HISTORY_TEMPLATE)
    history_js = _read(HISTORY_JS)

    assert "Последние запросы" in history_html
    assert "Ответ сформирован" in history_js
    assert "badge-status-complete" in history_js
