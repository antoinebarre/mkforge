"""MD036 checks for emphasis used as a heading substitute.

This rule belongs to Markdown verification because standalone bold or italic
text is sometimes used as an informal heading, which reduces document
structure and accessibility. It emits one diagnostic per line that consists
entirely of emphasis and does not end with configured punctuation.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    EMPHASIS_ONLY,
    _diagnostic,
)
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for emphasis-only lines used as headings.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for standalone emphasis that should be a heading.
    """
    punctuation = str(
        source.rule_options("MD036").get("punctuation", ".,;:!?"),
    )
    return tuple(
        _diagnostic(
            "MD036",
            line.number,
            1,
            "Use a heading instead of emphasis for sections.",
        )
        for line in lines_outside_fenced_code(source)
        if EMPHASIS_ONLY.match(line.text)
        and not line.text.rstrip().endswith(tuple(punctuation))
    )
