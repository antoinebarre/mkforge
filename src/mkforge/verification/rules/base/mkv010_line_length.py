"""MKV010: Line length.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.config import int_config
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV010"
NAME = "Line length"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report long lines.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    limit = int_config(context.rule_config(RULE_ID).get("line_length", 80), 80)
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line.number,
            f"Line exceeds {limit} characters.",
            MARKDOWN_CATEGORY,
        )
        for line in context.lines
        if len(line.text) > limit and " " in line.text[limit:]
    )
