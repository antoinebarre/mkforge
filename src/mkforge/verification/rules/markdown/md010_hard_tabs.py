"""MD010 checks for hard tab characters in Markdown source.

This rule belongs to Markdown verification because hard tabs produce
inconsistent indentation across editors and renderers. It emits one
diagnostic per line containing a tab character, optionally skipping
fenced code blocks.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _code_filtered_lines,
    _diagnostic,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines containing hard tab characters.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for hard-tab violations.
    """
    lines = _code_filtered_lines(source, "MD010", "ignore_code_blocks")
    return tuple(
        _diagnostic(
            "MD010",
            line.number,
            line.text.index("\t") + 1,
            "Replace hard tabs with spaces.",
        )
        for line in lines
        if "\t" in line.text
    )
