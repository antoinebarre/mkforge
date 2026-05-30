"""Table of contents generation for report trees."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.nodes import Section

if TYPE_CHECKING:
    from collections.abc import Sequence

    from mkforge.report import Report


def anchor_slug(title: str) -> str:
    """Convert a heading title to a GitHub-style anchor slug.

    Args:
        title: Raw heading title.

    Returns:
        Lowercase anchor slug.
    """
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug.strip())


def generate_toc(report: Report) -> str:
    """Generate a Markdown table of contents for a report.

    Args:
        report: Report to inspect.

    Returns:
        Markdown list linking to chapter and section headings.
    """
    lines: list[str] = []
    for chapter in report.children:
        lines.append(_toc_line(chapter.title, depth=1))
        _collect_section_lines(chapter.children, depth=2, lines=lines)
    return "\n".join(lines)


def _toc_line(title: str, depth: int) -> str:
    """Render one table of contents line.

    Args:
        title: Heading title.
        depth: One-based nesting depth.

    Returns:
        Markdown list item.
    """
    indent = "  " * (depth - 1)
    return f"{indent}- [{title}](#{anchor_slug(title)})"


def _collect_section_lines(
    children: Sequence[object],
    depth: int,
    lines: list[str],
) -> None:
    """Append table of contents lines for nested sections.

    Args:
        children: Candidate child nodes.
        depth: Current table of contents depth.
        lines: Mutable line accumulator.
    """
    for child in children:
        if isinstance(child, Section):
            lines.append(_toc_line(child.title, depth))
            _collect_section_lines(child.children, depth + 1, lines)
