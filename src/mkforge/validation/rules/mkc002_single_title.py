"""MKC002: Single top-level heading.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.categories import VALIDATION_CATEGORY
from mkforge.diagnostics.reporting import diagnostic

RULE_ID = "MKC002"
NAME = "Single top-level heading"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report documents with zero or multiple H1 headings.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    h1_headings = [
        heading for heading in context.headings if heading.level == 1
    ]
    if len(h1_headings) == 1:
        return ()
    line = h1_headings[1].line if h1_headings else 1
    message = "Document must contain exactly one level-1 title."
    return (diagnostic(RULE_ID, NAME, line, message, VALIDATION_CATEGORY),)
