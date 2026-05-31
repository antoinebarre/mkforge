"""Shared helpers for Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_api import MarkdownDiagnostic
from mkforge.markdown_lint_parser_patterns import HR_RE, LIST_RE
from mkforge.table_of_contents import anchor_slug

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import MarkdownLintContext


def diagnostic(
    rule_id: str,
    name: str,
    line: int,
    message: str,
    column: int = 1,
) -> MarkdownDiagnostic:
    """Create one Markdown diagnostic."""
    return MarkdownDiagnostic(rule_id, name, line, column, message)


def is_blank(text: str) -> bool:
    """Return whether a line is blank."""
    return not text.strip()


def is_list_item(text: str) -> bool:
    """Return whether a line is a Markdown list item."""
    return LIST_RE.match(text) is not None


def is_fence(text: str) -> bool:
    """Return whether a line starts a fenced code block."""
    return re.match(r"^\s*(`{3,}|~{3,})", text) is not None


def is_table_line(text: str) -> bool:
    """Return whether a line appears to be a GFM table row."""
    return "|" in text and bool(text.strip())


def is_horizontal_rule(text: str) -> bool:
    """Return whether a line appears to be a horizontal rule."""
    return HR_RE.match(text) is not None


def visible_text(text: str) -> str:
    """Return text with simple inline syntax removed."""
    value = re.sub(r"`[^`]*`", "", text)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    return re.sub(r"\[[^\]]+\]\([^)]+\)", "", value)


def heading_slugs(context: MarkdownLintContext) -> set[str]:
    """Return GitHub-like heading slugs for a context."""
    seen: dict[str, int] = {}
    slugs: set[str] = {"top"}
    for heading in context.headings:
        base = anchor_slug(heading.text)
        count = seen.get(base, 0)
        seen[base] = count + 1
        slugs.add(base if count == 0 else f"{base}-{count}")
    return slugs


def table_cells(text: str) -> list[str]:
    """Split a GFM table line into cells."""
    stripped = text.strip()
    stripped = stripped.removeprefix("|")
    stripped = stripped.removesuffix("|")
    return [cell.strip() for cell in stripped.split("|")]
