"""Table-oriented Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, is_table_line

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md055(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent table pipe style."""
    return tuple(
        diagnostic(
            "MD055",
            "Table pipe style",
            line.number,
            "Use consistent leading/trailing pipes.",
        )
        for line in context.lines
        if is_table_line(line.text) and _has_one_sided_pipe(line.text)
    )


def _has_one_sided_pipe(text: str) -> bool:
    """Return whether a table line uses only one outer pipe."""
    stripped = text.strip()
    return stripped.startswith("|") != stripped.endswith("|")
