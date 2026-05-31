"""MKV002: Heading style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV002"
NAME = "Heading style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed heading styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    if len({heading.style for heading in context.headings}) <= 1:
        return ()
    line = context.lines[0].number if context.lines else 1
    message = "Use one heading style."
    return (diagnostic(RULE_ID, NAME, line, message, MARKDOWN_CATEGORY),)
