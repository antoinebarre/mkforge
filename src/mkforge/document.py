"""Root report node for Markdown report generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from mkforge.errors import InvalidChildError
from mkforge.headings import Chapter, _validate_title

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class Report:
    """Root report document.

    Attributes:
        title: Non-empty report title.
        children: Ordered chapters.
        metadata: Optional YAML frontmatter dictionary.
        toc: Whether to render a table of contents.
        auto_numbering: Whether to number chapters and sections.
    """

    title: str
    children: list[Chapter] = field(default_factory=list)
    metadata: dict[str, object] | None = None
    toc: bool = False
    auto_numbering: bool = False

    def __post_init__(self) -> None:
        """Validate the report title."""
        _validate_title(self.title, "Report")

    def add(self, *items: Chapter) -> Report:
        """Append chapters and return this report.

        Args:
            *items: Chapters to append.

        Returns:
            This report instance.
        """
        for item in items:
            _validate_report_child(item)
            self.children.append(item)
        return self

    def render(self) -> str:
        """Render this report to Markdown.

        Returns:
            GitHub Flavored Markdown text.
        """
        from mkforge.markdown import render_report  # noqa: PLC0415

        return render_report(self)

    def save(self, path: str | Path) -> None:
        """Render this report to a UTF-8 Markdown file.

        Args:
            path: Destination Markdown file path.
        """
        from mkforge.markdown import save_report  # noqa: PLC0415

        save_report(self, path)


def _validate_report_child(child: object) -> None:
    """Validate a report child.

    Args:
        child: Candidate report child.
    """
    if not isinstance(child, Chapter):
        parent = "Report"
        raise InvalidChildError(parent, type(child).__name__)
