"""MKV018: Blockquote marker spaces.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import pattern_diagnostics

RULE_ID = "MKV018"
NAME = "Blockquote marker spaces"
PATTERN = re.compile(r"^>\s{2,}\S")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report multiple spaces after blockquote markers.

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
