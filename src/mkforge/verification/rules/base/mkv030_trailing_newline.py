"""MKV030: Single trailing newline.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV030"
NAME = "Single trailing newline"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report files not ending with exactly one newline.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    if context.source.endswith("\n") and not context.source.endswith("\n\n"):
        return ()
    line = max(1, len(context.lines))
    message = "End file with a single newline."
    return (diagnostic(RULE_ID, NAME, line, message, MARKDOWN_CATEGORY),)
