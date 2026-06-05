"""MKG005: Table column style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import GFM_CATEGORY
from mkforge.verification.tables import is_table_line

RULE_ID = "MKG005"
NAME = "Table column style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed GFM table column padding styles.

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
            "Use consistent table column spacing.",
            GFM_CATEGORY,
        )
        for line in context.lines
        if _has_mixed_padding(line.text)
    )


def _has_mixed_padding(text: str) -> bool:
    """Return whether a table row mixes padding styles.

    Args:
        text: Source line text.

    Returns:
        True when a table row mixes padding styles.
    """
    return is_table_line(text) and " |" not in text and "| " in text
