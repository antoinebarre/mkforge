"""Markdown heading parser for diagnostics."""

from __future__ import annotations

from mkforge.diagnostics.atx_headings import parse_atx_heading
from mkforge.diagnostics.models import Heading, Line
from mkforge.diagnostics.setext_headings import parse_setext_heading


def parse_headings(lines: tuple[Line, ...]) -> tuple[Heading, ...]:
    """Parse ATX and setext headings.

    Args:
        lines: Parsed source lines.

    Returns:
        Parsed headings.
    """
    headings: list[Heading] = []
    for index, line in enumerate(lines):
        heading = _heading_at(lines, index, line)
        if heading is not None:
            headings.append(heading)
    return tuple(headings)


def _heading_at(
    lines: tuple[Line, ...],
    index: int,
    line: Line,
) -> Heading | None:
    """Parse one possible heading.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.
        line: Parsed source line to inspect.

    Returns:
        Parsed heading, or None when the line is not a heading.
    """
    if line.in_code:
        return None
    heading = parse_atx_heading(line)
    return (
        heading if heading is not None else parse_setext_heading(lines, index)
    )
