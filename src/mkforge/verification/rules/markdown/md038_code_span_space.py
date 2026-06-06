"""MD038 checks spaces inside Markdown code span markers.

This rule belongs to Markdown verification because leading or trailing spaces
inside code span markers often indicate unintended code span text. It emits a
diagnostic for code spans with marker-adjacent whitespace.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD038"
NAME = "Code span marker spacing"
CODE_SPAN_WITH_INNER_SPACE = re.compile(r"`\s+[^`]*`|`[^`]*\s+`")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for code spans with inner spaces.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for code span marker spacing.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=CODE_SPAN_WITH_INNER_SPACE,
        rule_id=RULE_ID,
        name=NAME,
        message="Remove spaces just inside code span markers.",
    )
