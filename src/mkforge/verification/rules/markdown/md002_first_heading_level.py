"""MD002 checks that the first heading has the configured level.

This rule belongs to Markdown verification because the opening heading sets
the document root level. It emits one diagnostic when the first heading in
the document does not match the configured expected level.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _headings,
    _int_option,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return a diagnostic when the first heading level is wrong.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostic for a first heading whose level differs from the
        configured expected level, or an empty tuple when conforming.
    """
    headings = _headings(source)
    if not headings:
        return ()
    expected = _int_option(source, "MD002", "level", 1)
    first = headings[0]
    if first.level == expected:
        return ()
    return (
        _diagnostic(
            "MD002",
            first.line,
            1,
            f"First heading should be level {expected}.",
        ),
    )
