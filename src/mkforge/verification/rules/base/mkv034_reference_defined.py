"""MKV034: Reference links/images.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV034"
NAME = "Reference links/images"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report reference links/images whose labels are undefined.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    definitions = _reference_definitions(context)
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line,
            f"Reference label '{label}' is not defined.",
            MARKDOWN_CATEGORY,
        )
        for label, line in _reference_uses(context).items()
        if label not in definitions and label.lower() != "x"
    )


def _reference_definitions(context: SourceContext) -> dict[str, int]:
    """Return reference definition labels.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Reference definition labels.
    """
    definitions: dict[str, int] = {}
    for line in context.lines:
        match = re.match(r"^\[([^\]]+)\]:", line.text)
        if match:
            definitions.setdefault(match.group(1).lower(), line.number)
    return definitions


def _reference_uses(context: SourceContext) -> dict[str, int]:
    """Return referenced labels.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Referenced labels.
    """
    uses: dict[str, int] = {}
    for line in context.lines:
        for label in re.findall(r"!?\[[^\]]+\]\[([^\]]*)\]", line.text):
            if label:
                uses.setdefault(label.lower(), line.number)
    return uses
