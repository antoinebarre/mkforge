"""MKV014: Closed ATX missing space.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import pattern_diagnostics

RULE_ID = "MKV014"
NAME = "Closed ATX missing space"
PATTERN = re.compile(r"^#{1,6}\S.*#+$|^#{1,6} .*[^ ]#+$")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report missing spaces inside closed ATX heading markers.

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
