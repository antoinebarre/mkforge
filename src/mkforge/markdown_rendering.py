"""Internal traversal logic for Markdown report rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.frontmatter import render_metadata
from mkforge.headings import (
    Chapter,
    Section,
    compute_section_heading_level,
)
from mkforge.markdown_content import render_content
from mkforge.section_numbers import NumberingContext, numbered_title
from mkforge.table_of_contents import generate_toc

if TYPE_CHECKING:
    from collections.abc import Sequence

    from mkforge.document import Report


def render_report_blocks(report: Report) -> list[str]:
    """Render a report into Markdown blocks.

    Args:
        report: Report tree to render.

    Returns:
        Markdown block list.
    """
    parts = _initial_parts(report)
    context = NumberingContext() if report.auto_numbering else None
    _render_chapters(parts, report.children, context)
    return parts


def _initial_parts(report: Report) -> list[str]:
    """Build the leading document parts."""
    parts: list[str] = []
    if report.metadata is not None:
        parts.append(render_metadata(report.metadata))
    parts.append(f"# {report.title}")
    _append_toc(parts, report)
    return parts


def _append_toc(parts: list[str], report: Report) -> None:
    """Append a table of contents when requested."""
    if not report.toc:
        return
    toc = generate_toc(report)
    if toc:
        parts.append(toc)


def _render_chapters(
    parts: list[str],
    chapters: Sequence[Chapter],
    context: NumberingContext | None,
) -> None:
    """Append rendered chapters to a part list."""
    _enter_level(context)
    parts.extend(_render_chapter(chapter, context) for chapter in chapters)
    _leave_level(context)


def _render_chapter(chapter: Chapter, context: NumberingContext | None) -> str:
    """Render one chapter and its children."""
    title = _heading_title(chapter.title, context)
    parts = [f"## {title}"]
    _render_children(parts, chapter.children, depth=1, context=context)
    return "\n\n".join(parts)


def _render_children(
    parts: list[str],
    children: Sequence[object],
    depth: int,
    context: NumberingContext | None,
) -> None:
    """Append rendered child content."""
    _enter_level(context)
    parts.extend(_render_child(child, depth, context) for child in children)
    _leave_level(context)


def _render_child(
    child: object,
    depth: int,
    context: NumberingContext | None,
) -> str:
    """Render one child item."""
    if isinstance(child, Section):
        return _render_section(child, depth, context)
    return render_content(child)


def _render_section(
    section: Section,
    depth: int,
    context: NumberingContext | None,
) -> str:
    """Render one section and its children."""
    level = compute_section_heading_level(depth)
    title = _heading_title(section.title, context)
    parts = [f"{'#' * level} {title}"]
    _render_children(parts, section.children, depth + 1, context)
    return "\n\n".join(parts)


def _heading_title(title: str, context: NumberingContext | None) -> str:
    """Render a heading title with optional numbering."""
    if context is None:
        return title
    context.advance()
    return numbered_title(title, context)


def _enter_level(context: NumberingContext | None) -> None:
    """Enter a numbering level when numbering is enabled."""
    if context is not None:
        context.enter_level()


def _leave_level(context: NumberingContext | None) -> None:
    """Leave a numbering level when numbering is enabled."""
    if context is not None:
        context.leave_level()
