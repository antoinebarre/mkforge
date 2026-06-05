"""MD037 checks spaces inside Markdown emphasis markers.

This rule belongs to Markdown verification because spaces inside emphasis
markers commonly prevent the intended emphasis from being parsed. It emits a
diagnostic for emphasis spans whose marker directly encloses whitespace.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD037"
NAME = "Emphasis marker spacing"
EMPHASIS_WITH_INNER_SPACE = re.compile(
    r"(\*\*\s+\S.*?\s+\*\*|__\s+\S.*?\s+__|\*\s+\S.*?\s+\*|_\s+\S.*?\s+_)",
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for emphasis markers with inner spaces.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for emphasis marker spacing.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=EMPHASIS_WITH_INNER_SPACE,
        rule_id=RULE_ID,
        name=NAME,
        message="Remove spaces just inside emphasis markers.",
    )
