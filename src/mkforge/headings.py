"""Public Markdown heading extraction helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from mkforge.verification.policy import MarkdownLine, MarkdownSource
from mkforge.verification.rules.markdown._shared import ATX_HEADING
from mkforge.verification.source_scan import lines_outside_fenced_code


@dataclass(frozen=True)
class Heading:
    """Public Markdown heading extracted from source text.

    Attributes:
        line: One-based line number of the heading.
        level: Heading level from one to six.
        text: Heading text without ATX marker syntax.
    """

    line: int
    level: int
    text: str


def extract_headings(source: MarkdownSource) -> tuple[Heading, ...]:
    """Return ATX headings outside fenced code blocks.

    Args:
        source: Markdown source context.

    Returns:
        Public headings in document order.
    """
    headings: list[Heading] = []
    for line in lines_outside_fenced_code(source):
        match = ATX_HEADING.match(line.text)
        if match and match.group("mark").strip("#") == "":
            headings.append(_atx_heading(line, match))
    return tuple(headings)


def _atx_heading(line: MarkdownLine, match: re.Match[str]) -> Heading:
    """Return a public ATX heading for one source line.

    Args:
        line: Source line containing the heading.
        match: Regex match from the shared ATX heading pattern.

    Returns:
        Public Markdown heading with marker syntax removed.
    """
    body = match.group("body").strip()
    if body.endswith("#") and " #" in body:
        body = body.rstrip("#").strip()
    return Heading(line.number, len(match.group("mark")), body)
