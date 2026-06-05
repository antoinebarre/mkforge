"""Validation helpers for Markdown content elements."""

from __future__ import annotations

from typing import cast

from mkforge.input_checks import require_tuple


def validate_text_style(style: object) -> None:
    """Validate a text style.

    Args:
        style: Candidate style.
    """
    styles = {"plain", "bold", "italic", "code", "strikethrough"}
    if style not in styles:
        message = f"Text style must be one of {sorted(styles)}; got {style!r}."
        raise ValueError(message)


def validate_paragraph_content(
    content: object,
    inline_types: tuple[type[object], ...],
) -> None:
    """Validate paragraph content.

    Args:
        content: Candidate paragraph content.
        inline_types: Allowed inline item types.
    """
    if isinstance(content, str):
        _validate_paragraph_text(content)
        return
    if not isinstance(content, tuple):
        require_tuple(content, "Paragraph content")
    content_items = cast("tuple[object, ...]", content)
    for item in content_items:
        _validate_inline_item(item, inline_types)


def _validate_paragraph_text(content: str) -> None:
    """Validate paragraph plain text content."""
    if not content:
        message = "Paragraph content cannot be empty."
        raise ValueError(message)


def _validate_inline_item(
    item: object,
    inline_types: tuple[type[object], ...],
) -> None:
    """Validate one paragraph inline item."""
    if not isinstance(item, inline_types):
        message = (
            "Paragraph inline items must be Text or LineBreak; "
            f"got {type(item).__name__}."
        )
        raise TypeError(message)
