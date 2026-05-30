"""Chapter and section classes for Markdown report composition."""

from __future__ import annotations

from dataclasses import dataclass, field

from mkforge.content import CONTENT_TYPES, ContentElement
from mkforge.errors import InvalidChildError, ReportDepthError

MAX_HEADING_LEVEL = 6
_SECTION_BASE_LEVEL = 3


@dataclass
class Section:
    """Heading container rendered as H3 through H6.

    Attributes:
        title: Non-empty section title.
        children: Ordered sections or Markdown content elements.
    """

    title: str
    children: list[Section | ContentElement] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the section title."""
        _validate_title(self.title, "Section")

    def add(self, *items: Section | ContentElement) -> Section:
        """Append children and return this section.

        Args:
            *items: Valid section children.

        Returns:
            This section instance.
        """
        for item in items:
            _validate_container_child("Section", item)
            self.children.append(item)
        return self


@dataclass
class Chapter:
    """Top-level report container rendered as H2.

    Attributes:
        title: Non-empty chapter title.
        children: Ordered sections or Markdown content elements.
    """

    title: str
    children: list[Section | ContentElement] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the chapter title."""
        _validate_title(self.title, "Chapter")

    def add(self, *items: Section | ContentElement) -> Chapter:
        """Append children and return this chapter.

        Args:
            *items: Valid chapter children.

        Returns:
            This chapter instance.
        """
        for item in items:
            _validate_container_child("Chapter", item)
            self.children.append(item)
        return self


def compute_section_heading_level(depth_from_chapter: int) -> int:
    """Return the Markdown heading level for a section depth.

    Args:
        depth_from_chapter: One-based nesting depth below a chapter.

    Returns:
        Heading level between 3 and 6.
    """
    level = _SECTION_BASE_LEVEL + depth_from_chapter - 1
    if level > MAX_HEADING_LEVEL:
        raise ReportDepthError(level)
    return level


def _validate_title(title: str, label: str) -> None:
    """Validate a report container title.

    Args:
        title: Candidate title.
        label: Container type label.
    """
    if not title.strip():
        message = f"{label} title cannot be empty."
        raise ValueError(message)


def _validate_container_child(parent: str, child: object) -> None:
    """Validate a chapter or section child.

    Args:
        parent: Parent container label.
        child: Candidate child node.
    """
    if not isinstance(child, (Section, *CONTENT_TYPES)):
        raise InvalidChildError(parent, type(child).__name__)
