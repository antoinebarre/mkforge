"""MKV006: Trailing spaces.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV006"
NAME = "Trailing spaces"
HARD_BREAK_SPACES = 2


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report trailing spaces except two-space hard breaks.

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
            "Remove trailing spaces.",
            MARKDOWN_CATEGORY,
        )
        for line in context.lines
        if line.text.endswith(" ")
        and len(line.text) - len(line.text.rstrip(" ")) != HARD_BREAK_SPACES
    )
