"""GFM002 checks GitHub Flavored Markdown table column counts.

This rule belongs to GFM verification because the header row, delimiter row,
and body rows of a GFM table must use the same column count. It emits one
diagnostic when a row in a detected table has a different number of cells than
the table header.
"""

from __future__ import annotations

from mkforge.verification.policy import (
    Diagnostic,
    MarkdownLine,
    MarkdownSource,
)

RULE_ID = "GFM002"
NAME = "GFM table column count"


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for mismatched GFM table row widths.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for table rows with inconsistent column counts.
    """
    diagnostics: list[Diagnostic] = []
    lines = source.lines
    for index, line in enumerate(lines):
        if not _starts_table(lines, index):
            continue
        expected = len(_table_cells(line.text))
        for row in _table_rows(lines, index + 1):
            actual = len(_table_cells(row.text))
            if actual != expected:
                diagnostics.append(_diagnostic(row, expected, actual))
    return tuple(diagnostics)


def _starts_table(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a line starts a GFM table.

    Args:
        lines: Source lines.
        index: Zero-based candidate header index.

    Returns:
        True when the candidate line is followed by a delimiter row.
    """
    if index + 1 >= len(lines):
        return False
    return "|" in lines[index].text and _is_delimiter_row(
        lines[index + 1].text,
    )


def _table_rows(
    lines: tuple[MarkdownLine, ...],
    delimiter_index: int,
) -> tuple[MarkdownLine, ...]:
    """Return delimiter and body rows for a detected table.

    Args:
        lines: Source lines.
        delimiter_index: Zero-based table delimiter index.

    Returns:
        Contiguous table rows after the header.
    """
    rows: list[MarkdownLine] = []
    for line in lines[delimiter_index:]:
        if "|" not in line.text:
            break
        rows.append(line)
    return tuple(rows)


def _is_delimiter_row(text: str) -> bool:
    """Return whether a line can be a GFM delimiter row.

    Args:
        text: Source line text.

    Returns:
        True when the line is made only of delimiter-row characters.
    """
    stripped = text.strip()
    return (
        "|" in stripped
        and bool(stripped)
        and set(stripped) <= {"|", "-", ":", " "}
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


def _diagnostic(line: MarkdownLine, expected: int, actual: int) -> Diagnostic:
    """Return a table column-count diagnostic.

    Args:
        line: Source line with the mismatched row.
        expected: Expected table column count.
        actual: Actual row column count.

    Returns:
        Table column-count diagnostic.
    """
    return Diagnostic(
        rule_id=RULE_ID,
        name=NAME,
        line=line.number,
        column=1,
        message=f"GFM table row has {actual} cells; expected {expected}.",
    )
