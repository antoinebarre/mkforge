"""Helpers that classify and split GFM table lines."""


def is_table_line(text: str) -> bool:
    """Return whether a line appears to be a GFM table row.

    Args:
        text: Source line text.

    Returns:
        True when the line is non-empty and contains a pipe character.
    """
    return "|" in text and bool(text.strip())


def table_cells(text: str) -> list[str]:
    """Split a GFM table line into cells.

    Args:
        text: Source line text.

    Returns:
        Trimmed table cell values.
    """
    stripped = text.strip().removeprefix("|").removesuffix("|")
    return [cell.strip() for cell in stripped.split("|")]
