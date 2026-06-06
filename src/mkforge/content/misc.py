"""Miscellaneous block content elements: HorizontalRule and BlockQuote.

``HorizontalRule`` renders as a ``---`` separator.
``BlockQuote`` renders each line of its content with a ``> `` prefix.
"""

from __future__ import annotations

from dataclasses import dataclass

from mkforge.input_checks import require_string


@dataclass(frozen=True)
class HorizontalRule:
    """Horizontal separator rendered as ``---``."""

    def render(self) -> str:
        """Render the horizontal rule.

        Returns:
            The three-dash Markdown separator ``---``.
        """
        return "---"


@dataclass(frozen=True)
class BlockQuote:
    """Markdown block quote.

    Attributes:
        content: Block quote body text (may be empty).
    """

    content: str

    def __post_init__(self) -> None:
        """Validate block quote content."""
        require_string(self.content, "BlockQuote content", allow_empty=True)

    def render(self) -> str:
        """Render the block quote with ``> `` prefixes on each line.

        Returns:
            Block quote string with each line prefixed by ``> ``.
        """
        return "\n".join(f"> {line}" for line in self.content.splitlines())
