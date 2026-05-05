from __future__ import annotations

from app.services.ingestion.parser import parse_html_document


def test_parser_removes_navigation_blocks() -> None:
    html = """
    <html><body>
      <div id="docContent">
        <div class="navheader">Prev | Up | Next | Home</div>
        <div class="sect1">
          <h1>Logical Replication Overview</h1>
          <p>Logical replication lets you replicate selected tables and changes between PostgreSQL nodes safely.</p>
        </div>
        <div class="navfooter">Prev | Next</div>
      </div>
    </body></html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/16/logical-replication.html", html=html)

    assert any("Logical replication lets you replicate" in block.text for block in parsed.paragraphs)
    assert "prev" not in parsed.normalized_text.lower()
    assert "next" not in parsed.normalized_text.lower()
    assert "home" not in parsed.normalized_text.lower()


def test_parser_removes_global_layout_noise() -> None:
    html = """
    <html>
      <head>
        <style>.x { color: red; }</style>
        <script>console.log('noise')</script>
      </head>
      <body>
        <header>Global header text should not be indexed</header>
        <nav>Navigation area should not be indexed</nav>
        <main>
          <h1>Authentication</h1>
          <p>PostgreSQL checks pg_hba.conf records in order and applies the first matching rule.</p>
        </main>
        <form><input value="search" /></form>
        <footer>Footer text should not be indexed</footer>
      </body>
    </html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/16/auth-pg-hba-conf.html", html=html)

    normalized = parsed.normalized_text.lower()
    assert "pg_hba.conf records in order" in normalized
    assert "global header text" not in normalized
    assert "navigation area" not in normalized
    assert "footer text" not in normalized
    assert "console.log" not in normalized


def test_parser_preserves_code_blocks() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>SQL Example</h1>
      <pre>
SELECT slot_name, active
FROM pg_replication_slots
WHERE slot_type = 'logical';
      </pre>
    </div></body></html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/16/runtime-config-replication.html", html=html)

    code_blocks = [block for block in parsed.paragraphs if block.content_type == "code"]
    assert code_blocks
    assert any("SELECT slot_name" in block.text for block in code_blocks)
    assert any("\n" in block.text for block in code_blocks)


def test_parser_extracts_tables() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>Replication Parameters</h1>
      <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>wal_level</td><td>logical</td></tr>
        <tr><td>max_replication_slots</td><td>10</td></tr>
      </table>
    </div></body></html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/16/runtime-config-replication.html", html=html)

    tables = [block for block in parsed.paragraphs if block.content_type == "table"]
    assert tables
    table_text = tables[0].text
    assert "Parameter | Value" in table_text
    assert "wal_level | logical" in table_text
    assert "max_replication_slots | 10" in table_text


def test_parser_preserves_notes_warnings() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>Logical Replication Notes</h1>
      <div class="note"><p>Note: Ensure publisher and subscriber use compatible schema and replication settings.</p></div>
      <div class="warning"><p>Warning: Dropping a publication can break downstream subscriptions and requires careful rollout.</p></div>
    </div></body></html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/17/logical-replication.html", html=html)

    normalized = parsed.normalized_text.lower()
    assert "ensure publisher and subscriber" in normalized
    assert "dropping a publication can break" in normalized


def test_parser_does_not_duplicate_inline_code() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>Config</h1>
      <p>Set <code>wal_level</code> to logical before creating publications and subscriptions in production.</p>
    </div></body></html>
    """

    parsed = parse_html_document(source_url="https://www.postgresql.org/docs/16/runtime-config-replication.html", html=html)

    paragraph_blocks = [block for block in parsed.paragraphs if block.content_type == "paragraph"]
    code_blocks = [block for block in parsed.paragraphs if block.content_type == "code"]

    assert any("wal_level" in block.text for block in paragraph_blocks)
    assert not any(block.text.strip() == "wal_level" for block in code_blocks)


def test_parser_deduplicates_exact_blocks() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>Replication</h1>
      <p>Logical replication uses publications and subscriptions.</p>
      <p>Logical replication uses publications and subscriptions.</p>
    </div></body></html>
    """

    parsed = parse_html_document(
        source_url="https://www.postgresql.org/docs/16/logical-replication.html",
        html=html,
    )

    paragraph_blocks = [block for block in parsed.paragraphs if block.content_type == "paragraph"]
    matching = [
        block
        for block in paragraph_blocks
        if block.text == "Logical replication uses publications and subscriptions."
    ]
    assert len(matching) == 1


def test_parser_keeps_same_text_in_different_sections() -> None:
    html = """
    <html><body><div id="docContent">
      <h1>Section A</h1>
      <p>Same text with enough length for parser to keep it.</p>
      <h1>Section B</h1>
      <p>Same text with enough length for parser to keep it.</p>
    </div></body></html>
    """

    parsed = parse_html_document(
        source_url="https://www.postgresql.org/docs/16/logical-replication.html",
        html=html,
    )

    matching = [
        block
        for block in parsed.paragraphs
        if block.content_type == "paragraph"
        and block.text == "Same text with enough length for parser to keep it."
    ]
    assert len(matching) == 2
    assert {block.section_path for block in matching} == {"Section A", "Section B"}
