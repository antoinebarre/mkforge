"""MKV012: No space after hash.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import BAD_ATX_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV012"
NAME = "No space after hash"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report missing space after an ATX heading marker.

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
            "Add a space after heading marker.",
            MARKDOWN_CATEGORY,
        )
        for line in context.lines
        if BAD_ATX_RE.match(line.text)
    )
