"""MKC003: Trailing punctuation in heading.

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

RULE_ID = "MKC003"
NAME = "Trailing punctuation in heading"
PUNCTUATION = ".,;:!?"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report headings ending with configured punctuation.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    punctuation = str(
        context.rule_config(RULE_ID).get("punctuation", PUNCTUATION),
    )
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            heading.line,
            "Remove trailing punctuation from heading.",
            VALIDATION_CATEGORY,
        )
        for heading in context.headings
        if heading.text.endswith(tuple(punctuation))
    )
