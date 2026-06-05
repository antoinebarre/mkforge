"""Markdown content elements rendered inside reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mkforge.content_validation import (
    validate_paragraph_content,
    validate_text_style,
)
from mkforge.input_checks import require_string
from mkforge.table_validation import validate_items, validate_table

TextStyle = Literal["plain", "bold", "italic", "code", "strikethrough"]


@dataclass(frozen=True)
class Text:
    """Inline text with optional GitHub Flavored Markdown styling."""

    content: str
    style: TextStyle = "plain"

    def __post_init__(self) -> None:
        """Validate text content and style."""
        require_string(self.content, "Text content", allow_empty=True)
        validate_text_style(self.style)


@dataclass(frozen=True)
class LineBreak:
    """Inline hard line break within a paragraph."""


@dataclass(frozen=True)
class Paragraph:
    """Paragraph block containing plain text or inline content."""

    content: str | tuple[Text | LineBreak, ...]

    def __post_init__(self) -> None:
        """Validate that plain paragraph content is not empty."""
        validate_paragraph_content(self.content, (Text, LineBreak))


@dataclass(frozen=True)
class CodeBlock:
    """Fenced code block with an optional language hint."""

    code: str
    language: str = ""

    def __post_init__(self) -> None:
        """Validate code block fields."""
        require_string(self.code, "CodeBlock code", allow_empty=True)
        require_string(self.language, "CodeBlock language", allow_empty=True)


@dataclass(frozen=True)
class Table:
    """GitHub Flavored Markdown table."""

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        """Validate table dimensions."""
        validate_table(self.headers, self.rows)


@dataclass(frozen=True)
class BulletList:
    """Unordered Markdown list."""

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        validate_items(self.items, "BulletList")


@dataclass(frozen=True)
class NumberedList:
    """Ordered Markdown list."""

    items: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate that the list contains at least one item."""
        validate_items(self.items, "NumberedList")


@dataclass(frozen=True)
class Image:
    """Markdown image reference."""

    path: str
    alt: str = ""
    title: str = ""

    def __post_init__(self) -> None:
        """Validate image fields."""
        require_string(self.path, "Image path", allow_empty=False)
        require_string(self.alt, "Image alt", allow_empty=True)
        require_string(self.title, "Image title", allow_empty=True)


@dataclass(frozen=True)
class HorizontalRule:
    """Horizontal separator rendered as ``---``."""


@dataclass(frozen=True)
class BlockQuote:
    """Markdown block quote."""

    content: str

    def __post_init__(self) -> None:
        """Validate block quote content."""
        require_string(self.content, "BlockQuote content", allow_empty=True)


type ContentElement = (
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

CONTENT_TYPES = (
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
