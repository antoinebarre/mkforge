"""MKV003: Unordered list style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.patterns import LIST_RE
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV003"
NAME = "Unordered list style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report inconsistent unordered-list markers.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    markers = _unordered_markers(context)
    if len(set(markers)) <= 1:
        return ()
    line = context.lines[0].number if context.lines else 1
    message = "Use a consistent style."
    return (diagnostic(RULE_ID, NAME, line, message, MARKDOWN_CATEGORY),)


def _unordered_markers(context: SourceContext) -> list[str]:
    """Return unordered list marker characters.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Unordered list marker characters.
    """
    return [
        match.group(3)
        for line in context.lines
        if (match := LIST_RE.match(line.text)) and match.group(3)
    ]
