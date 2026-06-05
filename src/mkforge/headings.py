"""Chapter and section classes for Markdown report composition."""

from __future__ import annotations

from dataclasses import dataclass, field

from mkforge.content import CONTENT_TYPES, ContentElement
from mkforge.errors import InvalidChildError, ReportDepthError
from mkforge.input_checks import require_string

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
        _validate_children("Section", self.children)

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
        _validate_children("Chapter", self.children)

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
    _validate_section_depth(depth_from_chapter)
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
    require_string(title, f"{label} title", allow_empty=False)


def _validate_container_child(parent: str, child: object) -> None:
    """Validate a chapter or section child.

    Args:
        parent: Parent container label.
        child: Candidate child node.
    """
    if not isinstance(child, (Section, *CONTENT_TYPES)):
        raise InvalidChildError(parent, type(child).__name__)


def _validate_children(parent: str, children: object) -> None:
    """Validate initial container children.

    Args:
        parent: Parent container label.
        children: Candidate child list.
    """
    if not isinstance(children, list):
        message = (
            f"{parent} children must be a list; got {type(children).__name__}."
        )
        raise TypeError(message)
    for child in children:
        _validate_container_child(parent, child)


def _validate_section_depth(depth_from_chapter: object) -> None:
    """Validate a section depth input.

    Args:
        depth_from_chapter: Candidate section depth.
    """
    if not isinstance(depth_from_chapter, int):
        message = (
            "Section depth must be an int; "
            f"got {type(depth_from_chapter).__name__}."
        )
        raise TypeError(message)
    if depth_from_chapter < 1:
        message = "Section depth must be greater than or equal to 1."
        raise ValueError(message)
