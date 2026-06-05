"""MKC009: Proper names.

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
from mkforge.diagnostics.config import string_items
from mkforge.diagnostics.reporting import diagnostic

RULE_ID = "MKC009"
NAME = "Proper names"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report configured proper names written with wrong casing.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    names = string_items(context.rule_config(RULE_ID).get("names", []))
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line.number,
            f"Use proper casing for '{name}'.",
            VALIDATION_CATEGORY,
        )
        for line in context.lines
        for name in names
        if _has_wrong_case(line.text, name)
    )


def _has_wrong_case(text: str, name: str) -> bool:
    """Return whether text contains a name with wrong casing.

    Args:
        text: Source line text.
        name: Human-readable diagnostic name.

    Returns:
        True when text contains a name with wrong casing.
    """
    pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
    return any(match.group(0) != name for match in pattern.finditer(text))
