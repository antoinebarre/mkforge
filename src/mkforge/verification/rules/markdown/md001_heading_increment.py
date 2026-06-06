"""MD001 checks that heading levels increment by one.

This rule belongs to Markdown verification because headings form the document
structure and must not skip levels. It emits one diagnostic for each heading
whose level increases by more than one relative to the previous heading.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic, _headings


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for headings that skip a level.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for non-incremental heading level jumps.
    """
    diagnostics: list[Diagnostic] = []
    previous = 0
    for heading in _headings(source):
        if heading.level > previous + 1:
            diagnostics.append(
                _diagnostic(
                    "MD001",
                    heading.line,
                    1,
                    "Heading levels should increment by one.",
                ),
            )
        previous = heading.level
    return tuple(diagnostics)
