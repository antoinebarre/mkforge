"""MD003 checks that all headings use a consistent style.

This rule belongs to Markdown verification because mixed ATX and setext
heading styles reduce document consistency. It emits one diagnostic for
each heading whose style differs from the configured or detected expectation.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _expected_heading_style,
    _Heading,
    _heading_style_matches,
    _headings,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for headings that use a non-configured style.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for headings with inconsistent or unexpected style.
    """
    style = str(source.rule_options("MD003").get("style", "consistent"))
    headings = _headings(source)
    expected = _expected_heading_style(style, headings)
    return tuple(
        _diagnostic("MD003", heading.line, 1, f"Use {expected} heading style.")
        for heading in headings
        if expected
        and not _heading_style_matches(heading.style, heading.level, expected)
    )


__all__ = ["_Heading", "check"]
