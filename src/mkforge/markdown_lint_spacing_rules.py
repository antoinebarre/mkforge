"""Blank-line spacing Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, is_blank

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownHeading,
        MarkdownLine,
        MarkdownLintContext,
    )


def rule_md022(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report headings not surrounded by blank lines."""
    return tuple(
        diagnostic(
            "MD022",
            "Blanks around headings",
            heading.line,
            "Surround headings with blank lines.",
        )
        for heading in context.headings
        if not _heading_has_blank_lines(context.lines, heading)
    )


def _heading_has_blank_lines(
    lines: tuple[MarkdownLine, ...],
    heading: MarkdownHeading,
) -> bool:
    """Return whether a heading has acceptable surrounding lines."""
    index = heading.line - 1
    return _blank_before(lines, index) and _blank_after(lines, index)


def _blank_before(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a heading has a blank line before it."""
    return index == 0 or is_blank(lines[index - 1].text)


def _blank_after(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a heading has a blank line after it."""
    return index + 1 >= len(lines) or is_blank(lines[index + 1].text)
