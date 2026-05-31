"""Ordered-list Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic
from mkforge.markdown_lint_parser_patterns import LIST_RE

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md029(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report non-ordered ordered-list prefixes."""
    expected = 1
    diagnostics: list[MarkdownDiagnostic] = []
    for line in context.lines:
        expected, line_diagnostics = _check_ordered_line(
            expected,
            line.text,
            line.number,
        )
        diagnostics.extend(line_diagnostics)
    return tuple(diagnostics)


def rule_md030(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report spaces after list marker other than one."""
    return tuple(
        diagnostic(
            "MD030",
            "List marker space",
            line.number,
            "Use one space after list marker.",
        )
        for line in context.lines
        if (match := LIST_RE.match(line.text)) and len(match.group(5)) != 1
    )


def _ordered_list_diagnostic(line: int) -> MarkdownDiagnostic:
    """Return an ordered-list numbering diagnostic."""
    return diagnostic(
        "MD029",
        "Ordered list prefix",
        line,
        "Use increasing ordered-list numbers.",
    )


def _check_ordered_line(
    expected: int,
    text: str,
    line: int,
) -> tuple[int, tuple[MarkdownDiagnostic, ...]]:
    """Return next expected number and diagnostics for one line."""
    match = LIST_RE.match(text)
    if not match or not match.group(4):
        return 1, ()
    actual = int(match.group(4))
    diagnostics = _ordered_diagnostics(expected, actual, line)
    return actual + 1, diagnostics


def _ordered_diagnostics(
    expected: int,
    actual: int,
    line: int,
) -> tuple[MarkdownDiagnostic, ...]:
    """Return diagnostics for one ordered-list item."""
    if actual != expected:
        return (_ordered_list_diagnostic(line),)
    return ()
