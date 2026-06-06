"""Report document model: Report, Chapter, and Section.

A Report is the root of a report tree. It contains Chapters (rendered as H2),
which contain Sections (H3 through H6) and content elements. Sections nest up
to the Markdown H6 limit.

All container classes are mutable so children can be appended incrementally
via the fluent ``add`` method. Validation runs at construction time and on
every ``add`` call.

Import strategy
---------------
``render_report`` and ``save_report`` from ``mkforge.rendering`` are imported
inside ``Report.render`` and ``Report.save`` (annotated ``# noqa: PLC0415``).
This breaks the circular import:

    document → rendering  (Report.render calls render_report)
    rendering → document  (rendering needs Report/Chapter/Section types)

Deferred imports are the standard Python idiom for this pattern.  Do not
move them to the module level without verifying that the import cycle is
resolved by other means.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mkforge.content import CONTENT_TYPES, ContentElement
from mkforge.errors import InvalidChildError, ReportDepthError
from mkforge.input_checks import require_bool, require_metadata, require_string

MAX_HEADING_LEVEL = 6
_SECTION_BASE_LEVEL = 3


# ---------------------------------------------------------------------------
# Section and Chapter
# ---------------------------------------------------------------------------


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
        """Validate the section title and initial children."""
        _validate_title(self.title, "Section")
        _validate_container_children("Section", self.children)

    def add(self, *items: Section | ContentElement) -> Section:
        """Append children and return this section.

        Args:
            *items: Valid section children (``Section`` or content elements).

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
        """Validate the chapter title and initial children."""
        _validate_title(self.title, "Chapter")
        _validate_container_children("Chapter", self.children)

    def add(self, *items: Section | ContentElement) -> Chapter:
        """Append children and return this chapter.

        Args:
            *items: Valid chapter children (``Section`` or content elements).

        Returns:
            This chapter instance.
        """
        for item in items:
            _validate_container_child("Chapter", item)
            self.children.append(item)
        return self


# ---------------------------------------------------------------------------
# Report root
# ---------------------------------------------------------------------------


@dataclass
class Report:
    """Root report document.

    Attributes:
        title: Non-empty report title rendered as H1.
        children: Ordered chapters.
        metadata: Optional YAML frontmatter dictionary.
        toc: Whether to render a table of contents after the title.
        auto_numbering: Whether to prefix headings with dotted counters.
    """

    title: str
    children: list[Chapter] = field(default_factory=list)
    metadata: dict[str, object] | None = None
    toc: bool = False
    auto_numbering: bool = False

    def __post_init__(self) -> None:
        """Validate all report fields."""
        _validate_title(self.title, "Report")
        require_metadata(self.metadata)
        require_bool(self.toc, "Report toc")
        require_bool(self.auto_numbering, "Report auto_numbering")
        _validate_report_children(self.children)

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
        """Render this report to GitHub Flavored Markdown.

        Returns:
            Markdown document text.
        """
        from mkforge.rendering import render_report  # noqa: PLC0415

        return render_report(self)

    def save(self, path: str | Path, *, copy_assets: bool = False) -> None:
        """Render this report and write it to a UTF-8 Markdown file.

        Before writing, all local image paths in the report are verified to
        exist on disk.  When ``copy_assets`` is ``True``, images are copied
        into an ``assets/`` directory next to the output file and links are
        rewritten.

        Args:
            path: Destination Markdown file path.
            copy_assets: When ``True``, copy local images into ``assets/``
                and rewrite image links.  Defaults to ``False``.

        Raises:
            MissingAssetError: If any local image path does not exist on disk.
        """
        from mkforge.rendering import save_report  # noqa: PLC0415

        save_report(self, path, copy_assets=copy_assets)


# ---------------------------------------------------------------------------
# Heading level computation
# ---------------------------------------------------------------------------


def compute_section_heading_level(depth_from_chapter: int) -> int:
    """Return the Markdown heading level for a section at a given depth.

    Args:
        depth_from_chapter: One-based depth below the parent chapter (1 → H3).

    Returns:
        Heading level between 3 and 6.

    Raises:
        TypeError: If ``depth_from_chapter`` is not an integer.
        ValueError: If ``depth_from_chapter`` is less than 1.
        ReportDepthError: If the computed level would exceed H6.
    """
    _validate_section_depth(depth_from_chapter)
    level = _SECTION_BASE_LEVEL + depth_from_chapter - 1
    if level > MAX_HEADING_LEVEL:
        raise ReportDepthError(level)
    return level


# ---------------------------------------------------------------------------
# Private validation helpers
# ---------------------------------------------------------------------------


def _validate_title(title: str, label: str) -> None:
    """Validate a container title.

    Args:
        title: Candidate title string.
        label: Container type name for error messages.

    Raises:
        TypeError: If the title is not a string.
        ValueError: If the title is empty or blank.
    """
    require_string(title, f"{label} title", allow_empty=False)


def _validate_container_child(parent: str, child: object) -> None:
    """Validate one Chapter or Section child.

    Args:
        parent: Parent container label for error messages.
        child: Candidate child node.

    Raises:
        InvalidChildError: If the child is not a Section or content element.
    """
    if not isinstance(child, (Section, *CONTENT_TYPES)):
        raise InvalidChildError(parent, type(child).__name__)


def _validate_container_children(parent: str, children: object) -> None:
    """Validate the initial children list of a Chapter or Section.

    Args:
        parent: Parent container label for error messages.
        children: Candidate children list.

    Raises:
        TypeError: If children is not a list.
        InvalidChildError: If any child is invalid.
    """
    if not isinstance(children, list):
        message = (
            f"{parent} children must be a list; got {type(children).__name__}."
        )
        raise TypeError(message)
    for child in children:
        _validate_container_child(parent, child)


def _validate_report_child(child: object) -> None:
    """Validate one Report child.

    Args:
        child: Candidate report child.

    Raises:
        InvalidChildError: If the child is not a Chapter.
    """
    if not isinstance(child, Chapter):
        parent_label = "Report"
        raise InvalidChildError(parent_label, type(child).__name__)


def _validate_report_children(children: object) -> None:
    """Validate the initial children list of a Report.

    Args:
        children: Candidate chapter list.

    Raises:
        TypeError: If children is not a list.
        InvalidChildError: If any child is not a Chapter.
    """
    if not isinstance(children, list):
        message = (
            "Report children must be a list of Chapter; "
            f"got {type(children).__name__}."
        )
        raise TypeError(message)
    for child in children:
        _validate_report_child(child)


def _validate_section_depth(depth_from_chapter: object) -> None:
    """Validate a section depth input.

    Args:
        depth_from_chapter: Candidate depth value.

    Raises:
        TypeError: If the value is not an integer.
        ValueError: If the value is less than 1.
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
