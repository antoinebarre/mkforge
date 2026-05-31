"""MKV033: Strong style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV033"
NAME = "Strong style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed strong emphasis styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    source = "\n".join(line.text for line in context.lines if not line.in_code)
    if re.search(r"\*\*[^*]+\*\*", source) and re.search(r"__[^_]+__", source):
        message = "Use one strong emphasis style."
        return (diagnostic(RULE_ID, NAME, 1, message, MARKDOWN_CATEGORY),)
    return ()
