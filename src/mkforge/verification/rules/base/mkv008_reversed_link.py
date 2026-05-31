"""MKV008: Reversed link syntax.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV008"
NAME = "Reversed link syntax"
PATTERN = re.compile(r"\([^)]+\)\[[^\]]+\]")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report reversed link syntax.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return tuple(
        diagnostic(RULE_ID, NAME, line.number, NAME, MARKDOWN_CATEGORY)
        for line in context.lines
        if not line.in_code and PATTERN.search(line.text)
    )
