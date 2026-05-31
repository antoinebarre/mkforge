"""MKC005: Fenced code language.

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
from mkforge.verification.text import is_fence

RULE_ID = "MKC005"
NAME = "Fenced code language"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report fenced code blocks without a language identifier.

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
            "Specify a code fence language.",
            VALIDATION_CATEGORY,
        )
        for line in context.lines
        if is_fence(line.text) and not line.text.strip()[3:].strip()
    )
