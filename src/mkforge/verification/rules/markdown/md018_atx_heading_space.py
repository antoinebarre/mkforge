"""MD018 checks ATX heading opening marker spacing.

This rule belongs to Markdown verification because ATX heading markers require
whitespace after the opening marker to form a conforming heading. It emits one
diagnostic for each likely ATX heading missing that required whitespace.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD018"
NAME = "ATX heading marker spacing"
ATX_HEADING_WITHOUT_SPACE = re.compile(r"^ {0,3}#{1,6}(?=\S)")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for ATX headings missing marker spacing.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for missing ATX marker spacing.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=ATX_HEADING_WITHOUT_SPACE,
        rule_id=RULE_ID,
        name=NAME,
        message="Add a space after the ATX heading marker.",
    )
