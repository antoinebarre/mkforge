"""MKV031: Code fence style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import FENCE_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV031"
NAME = "Code fence style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed code fence styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    if len(_fence_markers(context)) <= 1:
        return ()
    message = "Use one code fence marker style."
    return (diagnostic(RULE_ID, NAME, 1, message, MARKDOWN_CATEGORY),)


def _fence_markers(context: SourceContext) -> set[str]:
    """Return code fence marker characters used by a source.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Code fence marker characters used by a source.
    """
    return {
        line.text.lstrip()[0]
        for line in context.lines
        if FENCE_RE.match(line.text)
    }
