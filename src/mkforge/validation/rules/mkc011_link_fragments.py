"""MKC011: Link fragments.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.anchors import heading_slugs, line_for_offset
from mkforge.verification.profiles import VALIDATION_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKC011"
NAME = "Link fragments"
FRAGMENT_RE = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report local link fragments that do not target a heading.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    slugs = heading_slugs(context)
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line_for_offset(context.source, match.start()),
            f"Link fragment '#{match.group(1)}' has no target.",
            VALIDATION_CATEGORY,
        )
        for match in FRAGMENT_RE.finditer(context.source)
        if match.group(1) not in slugs
    )
