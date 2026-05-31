"""MKC006: First line heading.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import VALIDATION_CATEGORY
from mkforge.verification.reporting import diagnostic
from mkforge.verification.text import is_blank

RULE_ID = "MKC006"
NAME = "First line heading"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report documents whose first content line is not an H1 title.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    first = next(
        (line for line in context.lines if not is_blank(line.text)),
        None,
    )
    if first is not None and first.text.startswith("# "):
        return ()
    message = "First content line must be a level-1 title."
    return (diagnostic(RULE_ID, NAME, 1, message, VALIDATION_CATEGORY),)
