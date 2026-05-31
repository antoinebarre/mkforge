"""MKC013: Descriptive link text.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.anchors import line_for_offset
from mkforge.verification.config import string_items
from mkforge.verification.profiles import VALIDATION_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKC013"
NAME = "Descriptive link text"
DEFAULT_PROHIBITED = ["click here", "here", "link", "more"]


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report generic link text.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    configured = context.rule_config(RULE_ID).get("prohibited_texts")
    prohibited = _prohibited(configured)
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line_for_offset(context.source, match.start()),
            "Use descriptive link text.",
            VALIDATION_CATEGORY,
        )
        for match in re.finditer(r"\[([^\]]+)\]\([^)]+\)", context.source)
        if match.group(1).strip().lower() in prohibited
    )


def _prohibited(value: object) -> set[str]:
    """Return prohibited link labels.

    Args:
        value: Candidate value.

    Returns:
        Prohibited link labels.
    """
    items = string_items(value) or DEFAULT_PROHIBITED
    return {item.lower() for item in items}
