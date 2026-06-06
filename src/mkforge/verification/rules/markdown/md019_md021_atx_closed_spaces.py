"""MD019 and MD021 check ATX heading marker spacing.

These two rules belong together because they both enforce single-space
padding around ATX heading markers:
- MD019: only one space is allowed after the opening marker.
- MD021: only one space is allowed inside closed ATX heading markers.
Each rule emits one diagnostic per non-conforming heading line.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic
from mkforge.verification.source_scan import lines_outside_fenced_code

_MULTIPLE_SPACES_AFTER = re.compile(r"^ {0,3}#{1,6} {2,}\S")
_MULTIPLE_SPACES_CLOSED = re.compile(
    r"^ {0,3}#{1,6} {2,}\S.*\s#{1,}\s*$"
    r"|^ {0,3}#{1,6}\s+\S.* {2,}#{1,}\s*$",
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD019 and MD021 ATX heading spacing diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for multiple spaces in ATX heading markers.
    """
    return (
        *_atx_multiple_spaces(source),
        *_closed_atx_multiple_spaces(source),
    )


def _atx_multiple_spaces(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD019 diagnostics for multiple spaces after ATX heading markers.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for headings with more than one space after the marker.
    """
    return tuple(
        _diagnostic(
            "MD019",
            line.number,
            1,
            "Use one space after the ATX heading marker.",
        )
        for line in lines_outside_fenced_code(source)
        if _MULTIPLE_SPACES_AFTER.match(line.text)
    )


def _closed_atx_multiple_spaces(
    source: MarkdownSource,
) -> tuple[Diagnostic, ...]:
    """Return MD021 diagnostics for multiple spaces inside closed ATX markers.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for closed ATX headings with non-single spacing.
    """
    return tuple(
        _diagnostic(
            "MD021",
            line.number,
            1,
            "Use one space inside closed ATX heading markers.",
        )
        for line in lines_outside_fenced_code(source)
        if _MULTIPLE_SPACES_CLOSED.match(line.text)
    )
