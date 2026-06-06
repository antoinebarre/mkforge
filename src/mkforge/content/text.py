"""Inline text content elements: Text and LineBreak.

Defines styled inline text and a hard line break for use inside paragraphs.
``Text`` supports plain, bold, italic, code, and strikethrough styles.
``LineBreak`` renders as a GFM hard line break (two trailing spaces + newline).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mkforge.input_checks import require_string

TextStyle = Literal["plain", "bold", "italic", "code", "strikethrough"]

_VALID_TEXT_STYLES: frozenset[str] = frozenset(
    {"plain", "bold", "italic", "code", "strikethrough"},
)

_TEXT_RENDERERS: dict[str, str] = {
    "plain": "{v}",
    "bold": "**{v}**",
    "italic": "*{v}*",
    "code": "`{v}`",
    "strikethrough": "~~{v}~~",
}


def _validate_text_style(style: object) -> None:
    """Validate a text style value.

    Args:
        style: Candidate style.

    Raises:
        ValueError: If the style is not one of the recognised values.
    """
    if style not in _VALID_TEXT_STYLES:
        message = (
            f"Text style must be one of {sorted(_VALID_TEXT_STYLES)}; "
            f"got {style!r}."
        )
        raise ValueError(message)


@dataclass(frozen=True)
class Text:
    """Inline text with optional GitHub Flavored Markdown styling.

    Attributes:
        content: Raw text content (may be empty).
        style: One of ``plain``, ``bold``, ``italic``, ``code``,
            ``strikethrough``.
    """

    content: str
    style: TextStyle = "plain"

    def __post_init__(self) -> None:
        """Validate text content and style."""
        require_string(self.content, "Text content", allow_empty=True)
        _validate_text_style(self.style)

    def render(self) -> str:
        """Render the inline text with its applied style.

        Returns:
            Styled Markdown inline string.
        """
        template = _TEXT_RENDERERS[self.style]
        return template.replace("{v}", self.content)


@dataclass(frozen=True)
class LineBreak:
    """Inline hard line break inside a paragraph.

    Rendered as two trailing spaces before the newline character.
    """

    def render(self) -> str:
        """Render the hard line break.

        Returns:
            Two trailing spaces followed by a newline.
        """
        return "  \n"


@dataclass(frozen=True)
class Link:
    """Inline hyperlink rendered as ``[text](url)`` or ``[text](url "title")``.

    Attributes:
        url: Link target URL or path (may not be empty).
        text: Visible link label (may be empty).
        title: Optional hover title (may be empty).
    """

    url: str
    text: str = ""
    title: str = ""

    def __post_init__(self) -> None:
        """Validate link fields."""
        require_string(self.url, "Link url", allow_empty=False)
        require_string(self.text, "Link text", allow_empty=True)
        require_string(self.title, "Link title", allow_empty=True)

    def render(self) -> str:
        """Render the hyperlink as a Markdown inline link.

        Returns:
            Markdown link syntax with optional title attribute.
        """
        title = f' "{self.title}"' if self.title else ""
        return f"[{self.text}]({self.url}{title})"
