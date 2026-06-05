"""MKV017: Heading start left.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import pattern_diagnostics
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV017"
NAME = "Heading start left"
PATTERN = re.compile(r"^\s+#{1,6}\s")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report headings that do not start at the beginning of a line.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return pattern_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        pattern=PATTERN,
        category=MARKDOWN_CATEGORY,
    )
