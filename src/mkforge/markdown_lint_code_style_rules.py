"""Code block and inline style Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic
from mkforge.markdown_lint_parser_patterns import FENCE_RE

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md046(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report mixed fenced and indented code block styles."""
    if _has_fenced_code(context) and _has_indented_code(context):
        return (
            diagnostic(
                "MD046",
                "Code block style",
                1,
                "Use one code block style.",
            ),
        )
    return ()


def rule_md048(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report mixed code fence styles."""
    markers = _fence_markers(context)
    if len(markers) > 1:
        return (
            diagnostic(
                "MD048",
                "Code fence style",
                1,
                "Use one code fence style.",
            ),
        )
    return ()


def _is_indented_code(text: str) -> bool:
    """Return whether text is an indented code line."""
    return text.startswith("    ") and bool(text.strip())


def _has_fenced_code(context: MarkdownLintContext) -> bool:
    """Return whether a document contains fenced code."""
    return any(FENCE_RE.match(line.text) for line in context.lines)


def _has_indented_code(context: MarkdownLintContext) -> bool:
    """Return whether a document contains indented code."""
    return any(_is_indented_code(line.text) for line in context.lines)


def _fence_markers(context: MarkdownLintContext) -> set[str]:
    """Return fence marker characters used by a document."""
    return {
        line.text.lstrip()[0]
        for line in context.lines
        if FENCE_RE.match(line.text)
    }
