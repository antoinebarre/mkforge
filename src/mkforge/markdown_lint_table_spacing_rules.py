"""Table spacing Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, is_blank, is_table_line

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLine,
        MarkdownLintContext,
    )


def rule_md058(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report tables not surrounded by blank lines."""
    return tuple(
        diagnostic(
            "MD058",
            "Blanks around tables",
            line.number,
            "Surround tables with blank lines.",
        )
        for index, line in enumerate(context.lines)
        if is_table_line(line.text)
        and not _table_has_blanks(context.lines, index)
    )


def rule_md060(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report mixed table column padding styles."""
    return tuple(
        diagnostic(
            "MD060",
            "Table column style",
            line.number,
            "Use consistent table column spacing.",
        )
        for line in context.lines
        if _has_mixed_padding(line.text)
    )


def _table_has_blanks(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a table line is surrounded by acceptable lines."""
    return _valid_before(lines, index) and _valid_after(lines, index)


def _valid_before(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a table line has an acceptable previous line."""
    if index == 0:
        return True
    text = lines[index - 1].text
    return is_blank(text) or is_table_line(text)


def _valid_after(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a table line has an acceptable next line."""
    if index + 1 >= len(lines):
        return True
    text = lines[index + 1].text
    return is_blank(text) or is_table_line(text)


def _has_mixed_padding(text: str) -> bool:
    """Return whether a table row mixes column padding styles."""
    return is_table_line(text) and " |" not in text and "| " in text
