"""MKG001: Bare URL.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import GFM_CATEGORY
from mkforge.verification.reporting import line_diagnostics
from mkforge.verification.text import visible_text

RULE_ID = "MKG001"
NAME = "Bare URL"
PATTERN = re.compile(r"(?<![<(])(https?://[^\s>)]+|[\w.+-]+@[\w.-]+\.\w+)")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report bare URLs that rely on GFM autolinking.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return line_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        category=GFM_CATEGORY,
        predicate=lambda line: (
            not line.in_code and bool(PATTERN.search(visible_text(line.text)))
        ),
    )
