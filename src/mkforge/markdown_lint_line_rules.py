"""Line-oriented Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, is_blank

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )

HARD_BREAK_SPACES = 2


def rule_md009(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report trailing spaces."""
    return tuple(
        diagnostic(
            "MD009",
            "Trailing spaces",
            line.number,
            "Remove trailing spaces.",
        )
        for line in context.lines
        if line.text.endswith(" ")
        and len(line.text) - len(line.text.rstrip(" ")) != HARD_BREAK_SPACES
    )


def rule_md010(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report hard tabs."""
    return tuple(
        diagnostic(
            "MD010",
            "Hard tabs",
            line.number,
            "Replace hard tabs with spaces.",
        )
        for line in context.lines
        if "\t" in line.text
    )


def rule_md011(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report reversed link syntax."""
    pattern = re.compile(r"\([^)]+\)\[[^\]]+\]")
    return _pattern_rule(context, "MD011", "Reversed link syntax", pattern)


def rule_md012(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report multiple consecutive blank lines."""
    diagnostics: list[MarkdownDiagnostic] = []
    blank_count = 0
    for line in context.lines:
        blank_count = _next_blank_count(
            blank_count,
            line.text,
            in_code=line.in_code,
        )
        if blank_count > 1:
            diagnostics.append(
                diagnostic(
                    "MD012",
                    "Multiple blank lines",
                    line.number,
                    "Remove extra blank line.",
                ),
            )
    return tuple(diagnostics)


def rule_md013(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report long lines."""
    limit = _int_config(context.rule_config("MD013").get("line_length", 80))
    return tuple(
        diagnostic(
            "MD013",
            "Line length",
            line.number,
            f"Line exceeds {limit} characters.",
        )
        for line in context.lines
        if len(line.text) > limit and " " in line.text[limit:]
    )


def rule_md047(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report files not ending with one newline."""
    if context.source.endswith("\n") and not context.source.endswith("\n\n"):
        return ()
    line = max(1, len(context.lines))
    return (
        diagnostic(
            "MD047",
            "Single trailing newline",
            line,
            "End file with a single newline.",
        ),
    )


def _next_blank_count(count: int, text: str, *, in_code: bool) -> int:
    """Return updated consecutive blank-line count."""
    return count + 1 if is_blank(text) and not in_code else 0


def _int_config(value: object) -> int:
    """Return an integer configuration value."""
    return int(value) if isinstance(value, str | int) else 80


def _pattern_rule(
    context: MarkdownLintContext,
    rule_id: str,
    name: str,
    pattern: re.Pattern[str],
) -> tuple[MarkdownDiagnostic, ...]:
    """Apply one regex pattern to non-code lines."""
    return tuple(
        diagnostic(rule_id, name, line.number, name)
        for line in context.lines
        if not line.in_code and pattern.search(line.text)
    )
