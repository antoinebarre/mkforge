"""Validation helpers for Markdown tables and item lists."""

from __future__ import annotations

from typing import cast

from mkforge.errors import InvalidTableError
from mkforge.validation import require_string, require_tuple


def validate_table(headers: object, rows: object) -> None:
    """Validate table dimensions and cell types.

    Args:
        headers: Candidate table headers.
        rows: Candidate table rows.
    """
    require_tuple(headers, "Table headers")
    require_tuple(rows, "Table rows")
    table_headers = cast("tuple[str, ...]", headers)
    table_rows = cast("tuple[tuple[str, ...], ...]", rows)
    _validate_headers(table_headers)
    for index, row in enumerate(table_rows):
        _validate_table_row(index, row, len(table_headers))


def validate_items(items: object, label: str) -> None:
    """Validate that list items are a non-empty string tuple.

    Args:
        items: Candidate item values.
        label: List type label for errors.
    """
    require_tuple(items, f"{label} items")
    tuple_items = cast("tuple[str, ...]", items)
    if not tuple_items:
        message = f"{label} must contain at least one item."
        raise ValueError(message)
    validate_string_items(tuple_items, f"{label} items")


def validate_string_items(items: tuple[str, ...], label: str) -> None:
    """Validate that tuple items are strings.

    Args:
        items: Candidate string tuple.
        label: Human-readable field label.
    """
    for index, item in enumerate(items):
        require_string(item, f"{label}[{index}]", allow_empty=True)


def _validate_headers(headers: tuple[str, ...]) -> None:
    """Validate table headers."""
    if not headers:
        message = "Table headers cannot be empty."
        raise InvalidTableError(message)
    validate_string_items(headers, "Table headers")


def _validate_table_row(index: int, row: object, width: int) -> None:
    """Validate one table row."""
    require_tuple(row, f"Table row {index}")
    table_row = cast("tuple[str, ...]", row)
    validate_string_items(table_row, f"Table row {index}")
    if len(table_row) != width:
        message = f"Row {index} has {len(table_row)} cells; expected {width}."
        raise InvalidTableError(message)
