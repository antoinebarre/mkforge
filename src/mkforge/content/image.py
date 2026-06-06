"""Image content element.

A Markdown image reference with a path, alternative text, and an optional
hover title.  The path is validated as a non-empty string; alt and title may
be empty.  MkForge does not validate, copy, or modify the path.
"""

from __future__ import annotations

from dataclasses import dataclass

from mkforge.input_checks import require_string


@dataclass(frozen=True)
class Image:
    """Markdown image reference.

    Attributes:
        path: Non-empty image path or URL.
        alt: Alternative text (may be empty).
        title: Optional hover title (may be empty).
    """

    path: str
    alt: str = ""
    title: str = ""

    def __post_init__(self) -> None:
        """Validate image fields."""
        require_string(self.path, "Image path", allow_empty=False)
        require_string(self.alt, "Image alt", allow_empty=True)
        require_string(self.title, "Image title", allow_empty=True)

    def render(self) -> str:
        """Render the image as a Markdown image reference.

        Returns:
            Markdown image syntax with optional title attribute.
        """
        title = f' "{self.title}"' if self.title else ""
        return f"![{self.alt}]({self.path}{title})"
