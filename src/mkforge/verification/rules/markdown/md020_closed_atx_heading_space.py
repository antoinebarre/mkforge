"""MD020 checks closed ATX heading marker spacing.

This rule belongs to Markdown verification because a closing ATX marker is only
valid when it is preceded by a space and followed only by spaces. It emits a
diagnostic when a line appears to use a closing marker without the required
space before it.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD020"
NAME = "Closed ATX heading spacing"
CLOSED_ATX_WITHOUT_SPACE = re.compile(
    r"^ {0,3}#{1,6}(?:\S.*#{1,}\s*$|\s+\S.*(?<!\s)#{1,}\s*$)",
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for closed ATX headings missing marker spacing.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for invalid closed ATX marker spacing.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=CLOSED_ATX_WITHOUT_SPACE,
        rule_id=RULE_ID,
        name=NAME,
        message="Add a space before the closing ATX heading marker.",
    )
