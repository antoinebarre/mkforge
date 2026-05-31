"""MKC001: Duplicate headings.

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

RULE_ID = "MKC001"
NAME = "Duplicate headings"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report repeated heading text.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    seen: set[str] = set()
    diagnostics: list[Diagnostic] = []
    for heading in context.headings:
        key = heading.text.lower()
        if key in seen:
            diagnostics.append(_diagnostic(heading.line))
        seen.add(key)
    return tuple(diagnostics)


def _diagnostic(line: int) -> Diagnostic:
    """Return a duplicate heading diagnostic.

    Args:
        line: One-based source line number.

    Returns:
        A duplicate heading diagnostic.
    """
    message = "Heading text is duplicated."
    return diagnostic(RULE_ID, NAME, line, message, VALIDATION_CATEGORY)
