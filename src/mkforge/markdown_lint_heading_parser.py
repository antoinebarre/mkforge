"""Heading parser helpers for Markdown linting."""

from __future__ import annotations

from mkforge.markdown_lint_api import MarkdownHeading, MarkdownLine
from mkforge.markdown_lint_parser_patterns import ATX_HEADING_RE
from mkforge.markdown_lint_setext_parser import setext_heading


def parse_headings(
    lines: tuple[MarkdownLine, ...],
) -> tuple[MarkdownHeading, ...]:
    """Parse ATX and setext headings."""
    headings: list[MarkdownHeading] = []
    for index, line in enumerate(lines):
        heading = _heading_at(lines, index, line)
        if heading is not None:
            headings.append(heading)
    return tuple(headings)


def _heading_at(
    lines: tuple[MarkdownLine, ...],
    index: int,
    line: MarkdownLine,
) -> MarkdownHeading | None:
    """Parse a heading at one line index."""
    if line.in_code:
        return None
    heading = _atx_heading(line)
    return heading if heading is not None else setext_heading(lines, index)


def _atx_heading(line: MarkdownLine) -> MarkdownHeading | None:
    """Parse one ATX heading."""
    match = ATX_HEADING_RE.match(line.text)
    if match is None:
        return None
    text = match.group(3).strip()
    return MarkdownHeading(line.number, len(match.group(1)), text, "atx")
