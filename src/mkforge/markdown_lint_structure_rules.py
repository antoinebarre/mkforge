"""Heading structure Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md001(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report skipped heading levels."""
    diagnostics: list[MarkdownDiagnostic] = []
    previous = 0
    for heading in context.headings:
        if previous and heading.level > previous + 1:
            diagnostics.append(
                diagnostic(
                    "MD001",
                    "Heading increment",
                    heading.line,
                    "Do not skip heading levels.",
                ),
            )
        previous = heading.level
    return tuple(diagnostics)


def rule_md003(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent heading styles."""
    styles = {heading.style for heading in context.headings}
    return (
        _whole_doc("MD003", "Heading style", context, "Use one heading style.")
        if len(styles) > 1
        else ()
    )


def _whole_doc(
    rule_id: str,
    name: str,
    context: MarkdownLintContext,
    message: str,
) -> tuple[MarkdownDiagnostic, ...]:
    """Return one whole-document diagnostic."""
    line = context.lines[0].number if context.lines else 1
    return (diagnostic(rule_id, name, line, message),)
