"""MD039 checks spaces inside Markdown link text brackets.

This rule belongs to Markdown verification because marker-adjacent spaces in
link text are usually unintended source syntax. It emits a diagnostic for links
whose visible text starts or ends with whitespace.
"""

from __future__ import annotations

import re

from mkforge.verification.diagnostic_pattern import matching_lines
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD039"
NAME = "Link text marker spacing"
LINK_TEXT_WITH_INNER_SPACE = re.compile(r"\[\s+[^\]]+]|\[[^\]]+\s+]\(")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for links with spaces inside text brackets.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for link text marker spacing.
    """
    return matching_lines(
        lines=lines_outside_fenced_code(source),
        pattern=LINK_TEXT_WITH_INNER_SPACE,
        rule_id=RULE_ID,
        name=NAME,
        message="Remove spaces just inside link text brackets.",
    )
