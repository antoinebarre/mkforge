"""Table content element.

A GitHub Flavored Markdown pipe table with a mandatory header row and zero
or more data rows.  All dimensions and cell types are validated at
construction time via ``InvalidTableError`` and ``TypeError``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from mkforge.errors import InvalidTableError
from mkforge.input_checks import require_string, require_tuple


def _validate_string_tuple(items: tuple[str, ...], label: str) -> None:
    """Validate that every element of a tuple is a string.

    Args:
        items: Candidate string tuple.
        label: Human-readable field label for error messages.

    Raises:
        TypeError: If any element is not a string.
    """
    for index, item in enumerate(items):
        require_string(item, f"{label}[{index}]", allow_empty=True)


def _validate_table(headers: object, rows: object) -> None:
    """Validate table headers and rows.

    Args:
        headers: Candidate table headers.
        rows: Candidate table rows.

    Raises:
        TypeError: If headers or rows are not tuples, or cells are not strings.
        InvalidTableError: If headers are empty or a row has the wrong cell
            count.
    """
    require_tuple(headers, "Table headers")
    require_tuple(rows, "Table rows")
    typed_headers = cast("tuple[str, ...]", headers)
    typed_rows = cast("tuple[tuple[str, ...], ...]", rows)
    if not typed_headers:
        message = "Table headers cannot be empty."
        raise InvalidTableError(message)
    _validate_string_tuple(typed_headers, "Table headers")
    for index, row in enumerate(typed_rows):
        require_tuple(row, f"Table row {index}")
        label = f"Table row {index}"
        _validate_string_tuple(row, label)
        if len(row) != len(typed_headers):
            message = (
                f"Row {index} has {len(row)} cells; "
                f"expected {len(typed_headers)}."
            )
            raise InvalidTableError(message)


def _table_row(cells: tuple[str, ...]) -> str:
    """Render one table row as a GFM pipe-delimited string.

    Args:
        cells: Cell strings.

    Returns:
        Pipe-delimited row string.
    """
    return "| " + " | ".join(cells) + " |"


@dataclass(frozen=True)
class Table:
    """GitHub Flavored Markdown table with a mandatory header row.

    Attributes:
        headers: Non-empty tuple of column header strings.
        rows: Zero or more data rows; each row must have the same cell count
            as ``headers``.
    """

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        """Validate table dimensions and cell types."""
        _validate_table(self.headers, self.rows)

    def render(self) -> str:
        """Render the table as a GFM pipe table.

        Returns:
            Multi-line pipe table string with header, separator, and rows.
        """
        separator = "| " + " | ".join("---" for _ in self.headers) + " |"
        lines = [_table_row(self.headers), separator]
        lines.extend(_table_row(row) for row in self.rows)
        return "\n".join(lines)
