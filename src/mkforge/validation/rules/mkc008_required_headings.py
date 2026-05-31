"""MKC008: Required heading structure.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.config import string_items
from mkforge.verification.profiles import VALIDATION_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKC008"
NAME = "Required heading structure"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report documents missing a configured heading sequence.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    required = string_items(context.rule_config(RULE_ID).get("headings", []))
    if not required:
        return ()
    actual = [
        f"{'#' * heading.level} {heading.text}" for heading in context.headings
    ]
    if actual[: len(required)] == required:
        return ()
    message = "Document heading sequence does not match required structure."
    return (diagnostic(RULE_ID, NAME, 1, message, VALIDATION_CATEGORY),)
