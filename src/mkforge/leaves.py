"""Leaf report nodes rendered as Markdown content blocks or inline text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mkforge.errors import InvalidTableError

TextStyle = Literal["plain", "bold", "italic", "code", "strikethrough"]


@dataclass(frozen=True)
class Text:
    """Inline text with optional GitHub Flavored Markdown styling."""

    content: str
    style: TextStyle = "plain"


@dataclass(frozen=True)
class LineBreak:
    """Inline hard line break within a paragraph."""


@dataclass(frozen=True)
class Paragraph:
    """Paragraph block containing plain text or inline nodes."""

    content: str | tuple[Text | LineBreak, ...]

    def __post_init__(self) -> None:
        """Validate that plain paragraph content is not empty."""
        if isinstance(self.content, str) and not self.content:
            message = "Paragraph content cannot be empty."
            raise ValueError(message)


@dataclass(frozen=True)
class CodeBlock:
    """Fenced code block with an optional language hint."""

    code: str
    language: str = ""


@dataclass(frozen=True)
class Table:
    """GitHub Flavored Markdown table."""

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        """Validate table dimensions."""
        if not self.headers:
            message = "Table headers cannot be empty."
            raise InvalidTableError(message)
        for index, row in enumerate(self.rows):
            _validate_row_width(index, row, len(self.headers))


@dataclass(frozen=True)
class BulletList:
    """Unordered Markdown list."""

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        _validate_items(self.items, "BulletList")


@dataclass(frozen=True)
class NumberedList:
    """Ordered Markdown list."""

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        _validate_items(self.items, "NumberedList")


@dataclass(frozen=True)
class Image:
    """Markdown image reference."""

    path: str
    alt: str = ""
    title: str = ""


@dataclass(frozen=True)
class HorizontalRule:
    """Horizontal separator rendered as ``---``."""


@dataclass(frozen=True)
class BlockQuote:
    """Markdown block quote."""

    content: str


type LeafNode = (
    Paragraph
    | Text
    | CodeBlock
    | Table
    | BulletList
    | NumberedList
    | Image
    | HorizontalRule
    | BlockQuote
)

LEAF_TYPES = (
    Paragraph,
    Text,
    CodeBlock,
    Table,
    BulletList,
    NumberedList,
    Image,
    HorizontalRule,
    BlockQuote,
)


def _validate_row_width(index: int, row: tuple[str, ...], width: int) -> None:
    """Validate one table row width.

    Args:
        index: Zero-based row index.
        row: Candidate row.
        width: Expected column count.
    """
    if len(row) != width:
        message = f"Row {index} has {len(row)} cells; expected {width}."
        raise InvalidTableError(message)


def _validate_items(items: tuple[str, ...], label: str) -> None:
    """Validate that a list has at least one item.

    Args:
        items: Candidate item values.
        label: List type label for errors.
    """
    if not items:
        message = f"{label} must contain at least one item."
        raise ValueError(message)
