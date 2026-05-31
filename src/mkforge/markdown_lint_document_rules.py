"""Document-level Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import (
    diagnostic,
    is_fence,
    is_horizontal_rule,
)

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md035(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent horizontal rule style."""
    markers = [
        line.text.strip()
        for line in context.lines
        if is_horizontal_rule(line.text)
    ]
    return _inconsistent("MD035", "Horizontal rule style", context, markers)


def rule_md036(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report emphasis-only paragraphs."""
    pattern = re.compile(r"^(\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_)$")
    return tuple(
        diagnostic(
            "MD036",
            "Emphasis as heading",
            line.number,
            "Use a heading instead of emphasis.",
        )
        for line in context.lines
        if pattern.match(line.text.strip())
    )


def rule_md040(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report fences without a language."""
    return tuple(
        diagnostic(
            "MD040",
            "Fenced code language",
            line.number,
            "Specify a code fence language.",
        )
        for line in context.lines
        if is_fence(line.text) and not line.text.strip()[3:].strip()
    )


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
