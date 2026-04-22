from __future__ import annotations

from dataclasses import dataclass

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


def parse_html_document(*, source_url: str, html: str, title_fallback: str | None = None) -> ParsedDocument:
    soup = BeautifulSoup(html, "lxml")

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

    heading_stack: dict[int, str] = {}
    paragraphs: list[ParagraphBlock] = []

    for node in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre"], recursive=True):
        if not isinstance(node, Tag):
            continue

        tag = node.name.lower()
        text = " ".join(node.get_text(" ", strip=True).split())
        if not text:
            continue

        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            level = int(tag[1])
            heading_stack[level] = text
            for cleanup in [k for k in heading_stack if k > level]:
                del heading_stack[cleanup]
            continue

        ordered_levels = sorted(heading_stack)
        if ordered_levels:
            section_path = " / ".join(heading_stack[level] for level in ordered_levels)
        else:
            section_path = title

        content_type = "code" if tag == "pre" else "paragraph"
        if len(text) < 30 and content_type == "paragraph":
            continue

        paragraphs.append(ParagraphBlock(section_path=section_path, text=text, content_type=content_type))

    normalized_text = "\n".join(f"[{p.section_path}] {p.text}" for p in paragraphs)
    return ParsedDocument(
        title=title,
        source_url=source_url,
        raw_html=html,
        normalized_text=normalized_text,
        paragraphs=paragraphs,
    )
