"""MKG002: Table pipe style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import GFM_CATEGORY
from mkforge.verification.reporting import line_diagnostics
from mkforge.verification.tables import is_table_line

RULE_ID = "MKG002"
NAME = "Table pipe style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report GFM table rows with inconsistent outer pipes.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return line_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        category=GFM_CATEGORY,
        predicate=lambda line: (
            is_table_line(line.text) and _has_one_outer_pipe(line.text)
        ),
    )


def _has_one_outer_pipe(text: str) -> bool:
    """Return whether a table line uses only one outer pipe.

    Args:
        text: Source line text.

    Returns:
        True when a table line uses only one outer pipe.
    """
    stripped = text.strip()
    return stripped.startswith("|") != stripped.endswith("|")
