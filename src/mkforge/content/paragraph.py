"""Paragraph content element.

A paragraph can hold either a plain text string or a structured sequence of
``Text`` and ``LineBreak`` inline elements.  Validation rejects empty plain
strings and non-conforming inline items at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from mkforge.content.text import LineBreak, Link, Text
from mkforge.input_checks import require_tuple

_INLINE_TYPES = (Text, LineBreak, Link)


def _validate_paragraph_content(content: object) -> None:
    """Validate paragraph content.

    Args:
        content: Candidate paragraph content — either a plain string or a
            tuple of ``Text``, ``LineBreak``, or ``Link`` items.

    Raises:
        TypeError: If the content is not a string or tuple.
        TypeError: If a tuple item is not ``Text``, ``LineBreak``, or ``Link``.
        ValueError: If the plain-string content is empty.
    """
    if isinstance(content, str):
        if not content:
            message = "Paragraph content cannot be empty."
            raise ValueError(message)
        return
    if not isinstance(content, tuple):
        require_tuple(content, "Paragraph content")
    for item in cast("tuple[object, ...]", content):
        if not isinstance(item, _INLINE_TYPES):
            message = (
                "Paragraph inline items must be Text, LineBreak, or Link; "
                f"got {type(item).__name__}."
            )
            raise TypeError(message)


@dataclass(frozen=True)
class Paragraph:
    """Paragraph block containing plain text or structured inline content.

    Attributes:
        content: Either a non-empty plain string or a tuple of ``Text``,
            ``LineBreak``, and ``Link`` items.
    """

    content: str | tuple[Text | LineBreak | Link, ...]

    def __post_init__(self) -> None:
        """Validate paragraph content."""
        _validate_paragraph_content(self.content)

    def render(self) -> str:
        """Render the paragraph to a Markdown block string.

        Returns:
            Plain text or joined inline element renders.
        """
        if isinstance(self.content, str):
            return self.content
        return "".join(item.render() for item in self.content)
