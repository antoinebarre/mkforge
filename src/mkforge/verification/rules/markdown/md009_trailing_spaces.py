"""MD009 checks for trailing spaces in Markdown source.

This rule belongs to Markdown verification because trailing whitespace is
invisible noise that causes unexpected hard line breaks when two spaces are
significant. It emits one diagnostic per line that has trailing spaces other
than an intentional hard-break count.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _int_option,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines with non-intentional trailing spaces.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for trailing-space violations.
    """
    allowed = _int_option(source, "MD009", "br_spaces", 2)
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        count = len(line.text) - len(line.text.rstrip(" "))
        if count and count != allowed:
            diagnostics.append(
                _diagnostic(
                    "MD009",
                    line.number,
                    len(line.text) - count + 1,
                    "Remove trailing spaces.",
                ),
            )
    return tuple(diagnostics)
