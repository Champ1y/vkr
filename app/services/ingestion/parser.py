from __future__ import annotations

from dataclasses import dataclass
import re

from bs4 import BeautifulSoup, Tag


@dataclass(slots=True)
class ParagraphBlock:
    section_path: str
    text: str
    content_type: str


@dataclass(slots=True)
class ParsedDocument:
    title: str
    source_url: str
    raw_html: str
    normalized_text: str
    paragraphs: list[ParagraphBlock]


_NOISE_TAGS = {
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "form",
    "button",
    "input",
    "select",
    "option",
    "aside",
}

_NOISE_SELECTORS = (
    ".navheader",
    ".navfooter",
    ".navlinks",
    ".breadcrumbs",
    ".breadcrumb",
    ".search",
    ".searchbox",
    ".sidebar",
    ".menu",
    ".toc",
    ".table-of-contents",
    "#pgHeader",
    "#pgFooter",
    "#pgSideWrap",
    "#docNav",
    "#pgSearch",
    "#pgContentWrap > nav",
)

_SERVICE_EXACT = {"prev", "next", "home", "up", "submit correction"}
_SERVICE_PREFIX = (
    "this page in other versions",
    "postgresql documentation",
    "copyright ©",
    "copyright (c)",
    "the postgresql global development group",
)
_NAV_TOKEN_RE = re.compile(r"[a-z]+")
_MIN_PARAGRAPH_LENGTH = 30


def _normalize_plain_text(text: str) -> str:
    return " ".join(text.split())


def _normalize_code_text(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    normalized: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip():
            blank_run = 0
            normalized.append(line)
            continue
        blank_run += 1
        if blank_run <= 1:
            normalized.append("")

    return "\n".join(normalized).strip()


def _table_to_text(table: Tag) -> str:
    rows: list[tuple[list[str], bool]] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        values = [_normalize_plain_text(cell.get_text(" ", strip=True)) for cell in cells]
        if not values or not any(values):
            continue
        rows.append((values, bool(row.find("th"))))

    if not rows:
        return ""

    lines: list[str] = []
    first_values, first_has_th = rows[0]
    if first_has_th:
        lines.append(" | ".join(first_values))
        data_rows = rows[1:]
    else:
        data_rows = rows

    for values, _ in data_rows:
        line = " | ".join(values)
        if line.strip():
            lines.append(line)

    return "\n".join(lines).strip()


def _is_service_noise(text: str) -> bool:
    plain = _normalize_plain_text(text)
    if not plain:
        return True

    lowered = plain.lower()
    if lowered in _SERVICE_EXACT:
        return True

    if len(plain) <= 140 and any(lowered.startswith(prefix) for prefix in _SERVICE_PREFIX):
        return True

    if len(plain) <= 40:
        nav_tokens = set(_NAV_TOKEN_RE.findall(lowered))
        if nav_tokens and nav_tokens.issubset({"prev", "next", "home", "up"}):
            return True

    return False


def _strip_noise(container: Tag | BeautifulSoup) -> None:
    for tag_name in _NOISE_TAGS:
        for node in container.find_all(tag_name):
            node.decompose()
    for selector in _NOISE_SELECTORS:
        for node in container.select(selector):
            node.decompose()


def parse_html_document(*, source_url: str, html: str, title_fallback: str | None = None) -> ParsedDocument:
    soup = BeautifulSoup(html, "lxml")
    _strip_noise(soup)

    title = ""
    h1 = soup.select_one("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    elif soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(strip=True)
    else:
        title = title_fallback or source_url

    root = (
        soup.select_one("div#docContent")
        or soup.select_one("main")
        or soup.select_one("article")
        or soup.body
        or soup
    )
    _strip_noise(root)

    heading_stack: dict[int, str] = {}
    paragraphs: list[ParagraphBlock] = []
    seen_blocks: set[tuple[str, str, str]] = set()

    for node in root.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "table", "code"],
        recursive=True,
    ):
        if not isinstance(node, Tag):
            continue

        tag = node.name.lower()

        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            text = _normalize_plain_text(node.get_text(" ", strip=True))
            if not text or _is_service_noise(text):
                continue
            level = int(tag[1])
            heading_stack[level] = text
            for cleanup in [k for k in heading_stack if k > level]:
                del heading_stack[cleanup]
            continue

        if tag == "code" and any(parent.name in {"p", "li", "pre", "table"} for parent in node.parents if isinstance(parent, Tag)):
            continue

        if tag == "pre":
            text = _normalize_code_text(node.get_text("\n", strip=False))
            content_type = "code"
        elif tag == "code":
            text = _normalize_code_text(node.get_text("\n", strip=False))
            content_type = "code"
        elif tag == "table":
            text = _table_to_text(node)
            content_type = "table"
        else:
            text = _normalize_plain_text(node.get_text(" ", strip=True))
            content_type = "paragraph"

        if not text or _is_service_noise(text):
            continue

        ordered_levels = sorted(heading_stack)
        if ordered_levels:
            section_path = " / ".join(heading_stack[level] for level in ordered_levels)
        else:
            section_path = title

        if content_type == "paragraph" and len(text) < _MIN_PARAGRAPH_LENGTH:
            continue

        dedupe_key = (
            section_path,
            content_type,
            " ".join(text.split()),
        )
        if dedupe_key in seen_blocks:
            continue
        seen_blocks.add(dedupe_key)

        paragraphs.append(ParagraphBlock(section_path=section_path, text=text, content_type=content_type))

    normalized_text = "\n".join(f"[{p.section_path}] {p.text}" for p in paragraphs)
    return ParsedDocument(
        title=title,
        source_url=source_url,
        raw_html=html,
        normalized_text=normalized_text,
        paragraphs=paragraphs,
    )
