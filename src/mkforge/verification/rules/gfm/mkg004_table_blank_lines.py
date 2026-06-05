"""MKG004: Blanks around tables.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, Line, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.diagnostics.text import is_blank
from mkforge.verification.profiles import GFM_CATEGORY
from mkforge.verification.tables import is_table_line

RULE_ID = "MKG004"
NAME = "Blanks around tables"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report GFM tables not surrounded by blank lines.

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
            "Surround tables with blank lines.",
            GFM_CATEGORY,
        )
        for index, line in enumerate(context.lines)
        if is_table_line(line.text)
        and not _table_has_blanks(context.lines, index)
    )


def _table_has_blanks(lines: tuple[Line, ...], index: int) -> bool:
    """Return whether a table row is surrounded by acceptable lines.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.

    Returns:
        True when a table row is surrounded by acceptable lines.
    """
    return _valid_before(lines, index) and _valid_after(lines, index)


def _valid_before(lines: tuple[Line, ...], index: int) -> bool:
    """Return whether the previous line is acceptable.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.

    Returns:
        True when the previous line is acceptable.
    """
    if index == 0:
        return True
    text = lines[index - 1].text
    return is_blank(text) or is_table_line(text)


def _valid_after(lines: tuple[Line, ...], index: int) -> bool:
    """Return whether the next line is acceptable.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.

    Returns:
        True when the next line is acceptable.
    """
    if index + 1 >= len(lines):
        return True
    text = lines[index + 1].text
    return is_blank(text) or is_table_line(text)
