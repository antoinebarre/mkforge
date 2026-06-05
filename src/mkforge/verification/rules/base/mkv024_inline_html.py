"""MKV024: Inline HTML.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import pattern_diagnostics
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV024"
NAME = "Inline HTML"
PATTERN = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(\s|>|/>)")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report inline HTML.

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
