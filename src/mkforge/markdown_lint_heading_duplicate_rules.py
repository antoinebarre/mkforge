"""Heading duplicate/count Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md024(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report duplicate headings."""
    seen: set[str] = set()
    diagnostics: list[MarkdownDiagnostic] = []
    for heading in context.headings:
        key = heading.text.lower()
        if key in seen:
            diagnostics.append(
                diagnostic(
                    "MD024",
                    "Duplicate heading",
                    heading.line,
                    "Use unique heading text.",
                ),
            )
        seen.add(key)
    return tuple(diagnostics)


def rule_md025(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report multiple H1 headings."""
    h1 = [heading for heading in context.headings if heading.level == 1]
    return tuple(
        diagnostic(
            "MD025",
            "Single H1",
            heading.line,
            "Use only one top-level heading.",
        )
        for heading in h1[1:]
    )
