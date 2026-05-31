"""Table column-count Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import (
    diagnostic,
    is_table_line,
    table_cells,
)

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md056(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent table column counts."""
    diagnostics: list[MarkdownDiagnostic] = []
    expected = 0
    for line in context.lines:
        expected, line_diagnostics = _check_table_line(
            expected,
            line.text,
            line.number,
        )
        diagnostics.extend(line_diagnostics)
    return tuple(diagnostics)


def _check_table_line(
    expected: int,
    text: str,
    line: int,
) -> tuple[int, tuple[MarkdownDiagnostic, ...]]:
    """Return expected column count and diagnostics for one table line."""
    if not is_table_line(text):
        return 0, ()
    count = len(table_cells(text))
    expected = expected or count
    return expected, _count_diagnostics(expected, count, line)


def _count_diagnostics(
    expected: int,
    count: int,
    line: int,
) -> tuple[MarkdownDiagnostic, ...]:
    """Return table column-count diagnostics."""
    if count != expected:
        return (
            diagnostic(
                "MD056",
                "Table column count",
                line,
                "Table row has inconsistent column count.",
            ),
        )
    return ()
