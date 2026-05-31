"""MKG003: Table column count.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import GFM_CATEGORY
from mkforge.verification.reporting import diagnostic
from mkforge.verification.tables import is_table_line, table_cells

RULE_ID = "MKG003"
NAME = "Table column count"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report GFM table rows with inconsistent column counts.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    diagnostics: list[Diagnostic] = []
    expected = 0
    for line in context.lines:
        expected, line_diagnostics = _check_line(
            expected,
            line.text,
            line.number,
        )
        diagnostics.extend(line_diagnostics)
    return tuple(diagnostics)


def _check_line(
    expected: int,
    text: str,
    line: int,
) -> tuple[int, tuple[Diagnostic, ...]]:
    """Return expected column count and diagnostics for one line.

    Args:
        expected: Expected table column count.
        text: Source line text.
        line: One-based source line number.

    Returns:
        Expected column count and diagnostics for one line.
    """
    if not is_table_line(text):
        return 0, ()
    count = len(table_cells(text))
    next_expected = expected or count
    return next_expected, _diagnostics(next_expected, count, line)


def _diagnostics(
    expected: int,
    count: int,
    line: int,
) -> tuple[Diagnostic, ...]:
    """Return table column count diagnostics.

    Args:
        expected: Expected table column count.
        count: Current count value.
        line: One-based source line number.

    Returns:
        Table column count diagnostics.
    """
    if count == expected:
        return ()
    message = "Table row has inconsistent column count."
    return (diagnostic(RULE_ID, NAME, line, message, GFM_CATEGORY),)
