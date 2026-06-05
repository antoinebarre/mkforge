"""MKV025: Horizontal rule style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.diagnostics.text import is_horizontal_rule
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV025"
NAME = "Horizontal rule style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report inconsistent horizontal rule style.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    markers = [
        line.text.strip()
        for line in context.lines
        if is_horizontal_rule(line.text)
    ]
    if len(set(markers)) <= 1:
        return ()
    line = context.lines[0].number if context.lines else 1
    message = "Use a consistent horizontal rule style."
    return (diagnostic(RULE_ID, NAME, line, message, MARKDOWN_CATEGORY),)
