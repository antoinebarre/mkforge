"""MD026 checks that headings do not end with trailing punctuation.

This rule belongs to Markdown verification because trailing punctuation
in headings is a common authoring mistake that reduces document
professionalism. It emits one diagnostic for each heading whose text ends
with one of the configured punctuation characters.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic, _headings


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for headings ending with trailing punctuation.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for headings with disallowed trailing punctuation.
    """
    punctuation = str(
        source.rule_options("MD026").get("punctuation", ".,;:!?"),
    )
    return tuple(
        _diagnostic(
            "MD026",
            heading.line,
            1,
            "Remove trailing punctuation from headings.",
        )
        for heading in _headings(source)
        if heading.text.rstrip().endswith(tuple(punctuation))
    )
