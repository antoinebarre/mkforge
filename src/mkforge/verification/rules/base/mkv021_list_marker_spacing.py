"""MKV021: List marker space.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import LIST_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV021"
NAME = "List marker space"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report spaces after list markers other than one.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line.number,
            "Use one space after list marker.",
            MARKDOWN_CATEGORY,
        )
        for line in context.lines
        if (match := LIST_RE.match(line.text)) and len(match.group(5)) != 1
    )
