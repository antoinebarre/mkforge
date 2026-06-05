"""MKC007: No empty links.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.categories import VALIDATION_CATEGORY
from mkforge.diagnostics.reporting import pattern_diagnostics

RULE_ID = "MKC007"
NAME = "No empty links"
PATTERN = re.compile(r"\[[^\]]+\]\((#?)\)")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report inline links with empty targets.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return pattern_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        pattern=PATTERN,
        category=VALIDATION_CATEGORY,
    )
