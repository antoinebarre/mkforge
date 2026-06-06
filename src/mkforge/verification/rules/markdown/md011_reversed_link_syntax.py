"""MD011 checks reversed Markdown link syntax.

This rule belongs to Markdown verification because reversed link syntax is not
parsed as a Markdown link. It emits a diagnostic for text that appears to swap
the link text brackets and destination parentheses.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD011"
NAME = "Reversed link syntax"
REVERSED_LINK = re.compile(r"\([^)]+\)\[[^\]]+]")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for reversed Markdown link syntax.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for reversed link syntax.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=REVERSED_LINK,
        rule_id=RULE_ID,
        name=NAME,
        message="Use [text](destination) Markdown link syntax.",
    )
