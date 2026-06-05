"""GFM001 checks GitHub Flavored Markdown table delimiter rows.

This rule belongs to GFM verification because a table delimiter row must
contain one delimiter cell for each table column, and each delimiter cell must
contain at least three hyphens with optional leading or trailing colons. It
emits one diagnostic for each malformed delimiter cell.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import (
    Diagnostic,
    MarkdownLine,
    MarkdownSource,
)

RULE_ID = "GFM001"
NAME = "GFM table delimiter"
DELIMITER_CELL = re.compile(r"^:?-{3,}:?$")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for malformed GFM table delimiter cells.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for malformed table delimiter cells.
    """
    return tuple(
        diagnostic
        for line in source.lines
        if _is_delimiter_candidate(line.text)
        for diagnostic in _delimiter_diagnostics(line)
    )


def _is_delimiter_candidate(text: str) -> bool:
    """Return whether a line looks like a GFM table delimiter row.

    Args:
        text: Source line text.

    Returns:
        True when the line uses only delimiter-row characters.
    """
    stripped = text.strip()
    return (
        "|" in stripped
        and bool(stripped)
        and set(stripped) <= {"|", "-", ":", " "}
    )


def _delimiter_diagnostics(line: MarkdownLine) -> tuple[Diagnostic, ...]:
    """Return delimiter-cell diagnostics for one candidate row.

    Args:
        line: Candidate delimiter line.

    Returns:
        Diagnostics for malformed delimiter cells.
    """
    cells = _table_cells(line.text)
    return tuple(
        Diagnostic(
            rule_id=RULE_ID,
            name=NAME,
            line=line.number,
            column=1,
            message=(
                "Use at least three hyphens in each GFM table delimiter cell."
            ),
        )
        for cell in cells
        if not DELIMITER_CELL.fullmatch(cell.strip())
    )


def _table_cells(text: str) -> tuple[str, ...]:
    """Return table cells without optional outer empty pipe cells.

    Args:
        text: Raw table row text.

    Returns:
        Table cells without syntactic outer pipe cells.
    """
    cells = text.strip().split("|")
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return tuple(cells)
