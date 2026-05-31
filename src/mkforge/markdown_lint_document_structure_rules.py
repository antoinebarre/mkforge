"""Document heading-structure Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, is_blank

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md041(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report missing first-line H1."""
    first = next(
        (line for line in context.lines if not is_blank(line.text)),
        None,
    )
    if first is None or first.text.startswith("# "):
        return ()
    return (
        diagnostic(
            "MD041",
            "First line H1",
            first.number,
            "Start the file with an H1 heading.",
        ),
    )


def rule_md043(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report required heading structure mismatches."""
    expected = tuple(
        _string_items(context.rule_config("MD043").get("headings", [])),
    )
    actual = tuple(
        "#" * heading.level + " " + heading.text
        for heading in context.headings
    )
    return _structure_mismatch(context, expected, actual)


def _structure_mismatch(
    context: MarkdownLintContext,
    expected: tuple[str, ...],
    actual: tuple[str, ...],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return required-heading mismatch diagnostic."""
    if not expected or expected == actual:
        return ()
    line = context.headings[0].line if context.headings else 1
    return (
        diagnostic(
            "MD043",
            "Required headings",
            line,
            "Headings do not match required structure.",
        ),
    )


def _string_items(value: object) -> list[str]:
    """Return string values from a sequence-like configuration value."""
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value]
    return []
