"""Unordered-list Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic
from mkforge.markdown_lint_parser_patterns import LIST_RE

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md004(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent unordered list markers."""
    markers = [
        match.group(3)
        for line in context.lines
        if (match := LIST_RE.match(line.text)) and match.group(3)
    ]
    return _inconsistent("MD004", "Unordered list style", context, markers)


def _inconsistent(
    rule_id: str,
    name: str,
    context: MarkdownLintContext,
    values: list[str],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return one diagnostic if values are inconsistent."""
    if len(set(values)) <= 1:
        return ()
    line = context.lines[0].number if context.lines else 1
    return (diagnostic(rule_id, name, line, "Use a consistent style."),)
