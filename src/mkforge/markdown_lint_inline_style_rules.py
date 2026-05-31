"""Inline style consistency Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md049(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report mixed emphasis styles."""
    return _mixed_inline_style(
        context,
        "MD049",
        "Emphasis style",
        r"(?<!\*)\*[^*]+\*(?!\*)",
        r"(?<!_)_[^_]+_(?!_)",
    )


def rule_md050(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report mixed strong styles."""
    return _mixed_inline_style(
        context,
        "MD050",
        "Strong style",
        r"\*\*[^*]+\*\*",
        r"__[^_]+__",
    )


def _mixed_inline_style(
    context: MarkdownLintContext,
    rule_id: str,
    name: str,
    first_pattern: str,
    second_pattern: str,
) -> tuple[MarkdownDiagnostic, ...]:
    """Return a diagnostic when both inline styles are present."""
    source = "\n".join(line.text for line in context.lines if not line.in_code)
    if re.search(first_pattern, source) and re.search(second_pattern, source):
        return (diagnostic(rule_id, name, 1, "Use one inline style."),)
    return ()
