"""List content elements: BulletList and NumberedList.

Unordered and ordered Markdown lists backed by non-empty string tuples.
Both types validate their items at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from mkforge.input_checks import require_string, require_tuple


def _validate_list_items(items: object, label: str) -> None:
    """Validate list items are a non-empty tuple of strings.

    Args:
        items: Candidate item values.
        label: List type label for error messages.

    Raises:
        TypeError: If items is not a tuple or contains non-strings.
        ValueError: If the tuple is empty.
    """
    require_tuple(items, f"{label} items")
    typed = cast("tuple[str, ...]", items)
    if not typed:
        message = f"{label} must contain at least one item."
        raise ValueError(message)
    for index, item in enumerate(typed):
        require_string(item, f"{label} items[{index}]", allow_empty=True)


@dataclass(frozen=True)
class BulletList:
    """Unordered Markdown list.

    Attributes:
        items: Non-empty tuple of list item strings.
    """

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        _validate_list_items(self.items, "BulletList")

    def render(self) -> str:
        """Render the bullet list as a Markdown unordered list.

        Returns:
            Newline-separated list items prefixed with ``- ``.
        """
        return "\n".join(f"- {item}" for item in self.items)


@dataclass(frozen=True)
class NumberedList:
    """Ordered Markdown list numbered from 1.

    Attributes:
        items: Non-empty tuple of list item strings.
    """

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        _validate_list_items(self.items, "NumberedList")

    def render(self) -> str:
        """Render the numbered list as a Markdown ordered list.

        Returns:
            Newline-separated list items numbered from 1.
        """
        return "\n".join(
            f"{i}. {item}" for i, item in enumerate(self.items, start=1)
        )
