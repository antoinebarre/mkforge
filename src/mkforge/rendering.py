"""Markdown rendering pipeline for report trees.

Converts a Report tree into a GitHub Flavored Markdown document.  The module
owns the complete rendering responsibility: YAML frontmatter, headings, table
of contents, automatic heading numbering, and every content element type.

Public entry points are ``render_report`` (returns a string) and
``save_report`` (writes to a file).

Import strategy
---------------
``Report``, ``Chapter``, ``Section``, and ``assets.*`` are imported inside
functions rather than at module level (annotated ``# noqa: PLC0415``).  This
breaks the circular import that would otherwise arise from:

    document → rendering  (document.Report.render calls render_report)
    rendering → document  (rendering needs Report/Chapter/Section types)
    rendering → assets    (save_report calls asset helpers)
    assets → document     (asset walkers check isinstance
                           Report/Chapter/Section)

Deferred imports are the standard Python idiom for this pattern.  Do not
move them to the module level without verifying that the import cycle is
resolved by other means.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from mkforge.content import Renderable
from mkforge.input_checks import require_metadata, require_path, require_string

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_report(report: object) -> str:
    """Render a report to GitHub Flavored Markdown.

    Args:
        report: Report tree to render.

    Returns:
        Markdown document text.

    Raises:
        TypeError: If ``report`` is not a ``Report`` instance.
    """
    _validate_report(report)
    from mkforge.document import Report  # noqa: PLC0415

    typed = cast("Report", report)
    return "\n\n".join(_report_blocks(typed))


def save_report(
    report: object,
    path: str | Path,
    *,
    copy_assets: bool = False,
) -> None:
    """Render a report and write it to a UTF-8 Markdown file.

    Before writing, all local image paths referenced in the report are
    verified to exist on disk.  If ``copy_assets`` is ``True``, images are
    copied into an ``assets/`` directory next to the output file and image
    references in the Markdown are rewritten accordingly.

    Args:
        report: Report tree to render.
        path: Destination path.
        copy_assets: When ``True``, copy local images into ``assets/`` next
            to the output file and rewrite image links.  Defaults to
            ``False``.

    Raises:
        TypeError: If ``report`` is not a ``Report`` instance.
        TypeError: If ``path`` is not a string or ``PathLike``.
        ValueError: If ``path`` is blank.
        MissingAssetError: If any local image path does not exist on disk.
    """
    from mkforge.assets import (  # noqa: PLC0415
        collect_local_image_paths,
        collect_remote_image_urls,
        copy_assets_to_dir,
        download_assets_to_dir,
        rewrite_image_paths,
        verify_assets,
    )

    _validate_report(report)
    require_path(path, "save path")
    destination = Path(path)

    local_paths = collect_local_image_paths(report)
    verify_assets(local_paths)

    markdown = render_report(report)

    if copy_assets:
        assets_dir = destination.parent / "assets"
        local_map: dict[Path, str] = {}
        remote_map: dict[str, str] = {}
        if local_paths:
            local_map = copy_assets_to_dir(local_paths, assets_dir)
        remote_urls = collect_remote_image_urls(report)
        if remote_urls:
            remote_map = download_assets_to_dir(remote_urls, assets_dir)
        if local_map or remote_map:
            markdown = rewrite_image_paths(markdown, local_map, remote_map)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")


# ---------------------------------------------------------------------------
# Heading numbering
# ---------------------------------------------------------------------------


@dataclass
class NumberingContext:
    """Track heading counters while traversing a report tree.

    Attributes:
        counters: Current stack of per-level sibling counters.
    """

    counters: list[int] = field(default_factory=list)

    def enter_level(self) -> None:
        """Push a new zero counter onto the stack."""
        self.counters.append(0)

    def leave_level(self) -> None:
        """Pop the current level counter from the stack."""
        self.counters.pop()

    def advance(self) -> None:
        """Increment the counter for the current level."""
        self.counters[-1] += 1

    def prefix(self) -> str:
        """Return the dotted numbering prefix for the current heading.

        Returns:
            A dotted prefix such as ``1.2.``.
        """
        return ".".join(str(c) for c in self.counters) + "."


def _numbered_title(title: str, context: NumberingContext) -> str:
    """Prefix a heading title with the current numbering context.

    Args:
        title: Raw heading title.
        context: Active numbering context.

    Returns:
        Numbered heading title such as ``1.2. Introduction``.
    """
    return f"{context.prefix()} {title}"


# ---------------------------------------------------------------------------
# Table of contents
# ---------------------------------------------------------------------------


def anchor_slug(title: str) -> str:
    """Convert a heading title to a GitHub-style anchor slug.

    Args:
        title: Raw heading title.

    Returns:
        Lowercase, hyphen-separated anchor slug.
    """
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug.strip())


def _generate_toc(report: object) -> str:
    """Generate a Markdown table of contents for a report.

    Args:
        report: Report whose chapters and sections are enumerated.

    Returns:
        Markdown list linking to chapter and section headings, or an empty
        string when the report has no chapters.
    """
    from mkforge.document import Report  # noqa: PLC0415

    typed = cast("Report", report)
    lines: list[str] = []
    for chapter in typed.children:
        lines.append(_toc_line(chapter.title, depth=1))
        _collect_section_lines(chapter.children, depth=2, lines=lines)
    return "\n".join(lines)


def _toc_line(title: str, depth: int) -> str:
    """Render one table of contents entry.

    Args:
        title: Heading title.
        depth: One-based nesting depth (1 for chapters, 2+ for sections).

    Returns:
        Indented Markdown list item with an anchor link.
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
        children: Candidate child nodes of a Chapter or Section.
        depth: Current table of contents depth.
        lines: Mutable line accumulator.
    """
    from mkforge.document import Section  # noqa: PLC0415

    for child in children:
        if isinstance(child, Section):
            lines.append(_toc_line(child.title, depth))
            _collect_section_lines(child.children, depth + 1, lines)


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------


def _render_metadata(metadata: dict[str, object]) -> str:
    """Render metadata as a YAML frontmatter block.

    Args:
        metadata: Dictionary to serialise.

    Returns:
        YAML frontmatter block delimited by ``---`` lines.
    """
    require_metadata(metadata)
    lines = ["---"]
    for key, value in metadata.items():
        _append_metadata_value(lines, key, value)
    lines.append("---")
    return "\n".join(lines)


def _append_metadata_value(lines: list[str], key: str, value: object) -> None:
    """Append one metadata key-value pair to the frontmatter lines.

    Args:
        lines: Mutable line accumulator.
        key: Metadata key.
        value: Metadata value (scalar, list, or tuple).
    """
    require_string(key, "metadata key", allow_empty=False)
    if isinstance(value, list | tuple):
        lines.append(f"{key}:")
        lines.extend(f"  - {_scalar_text(item)}" for item in value)
        return
    lines.append(f"{key}: {_scalar_text(value)}")


def _scalar_text(value: object) -> str:
    """Render a scalar metadata value to its YAML text form.

    Args:
        value: Scalar value to render.

    Returns:
        YAML-compatible text representation.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


# ---------------------------------------------------------------------------
# Content element renderers
# ---------------------------------------------------------------------------


def render_content_element(node: object) -> str:
    """Render one content element to a Markdown block string.

    Each content element type owns its ``render() -> str`` method.  This
    function validates the protocol contract and delegates to it.

    Args:
        node: Content element to render.

    Returns:
        Rendered Markdown block.

    Raises:
        TypeError: If the node does not implement the ``Renderable`` protocol.
    """
    if not isinstance(node, Renderable):
        message = f"Unknown content type: {type(node).__name__}"
        raise TypeError(message)
    return node.render()


# ---------------------------------------------------------------------------
# Report tree traversal
# ---------------------------------------------------------------------------


def _report_blocks(report: object) -> list[str]:
    """Render a report into an ordered list of Markdown block strings.

    Args:
        report: Report tree to traverse.

    Returns:
        Ordered Markdown blocks joined by two newlines by the caller.
    """
    from mkforge.document import Report  # noqa: PLC0415

    typed = cast("Report", report)
    parts: list[str] = []
    if typed.metadata is not None:
        parts.append(_render_metadata(typed.metadata))
    parts.append(f"# {typed.title}")
    if typed.toc:
        toc = _generate_toc(typed)
        if toc:
            parts.append(toc)
    context = NumberingContext() if typed.auto_numbering else None
    _render_chapters(parts, typed.children, context)
    return parts


def _render_chapters(
    parts: list[str],
    chapters: Sequence[object],
    context: NumberingContext | None,
) -> None:
    """Append rendered chapters to the block list.

    Args:
        parts: Mutable block accumulator.
        chapters: Chapter sequence to render.
        context: Active numbering context, or ``None``.
    """
    _enter_level(context)
    parts.extend(_render_chapter(chapter, context) for chapter in chapters)
    _leave_level(context)


def _render_chapter(chapter: object, context: NumberingContext | None) -> str:
    """Render one chapter and its children to a Markdown block string.

    Args:
        chapter: Chapter instance.
        context: Active numbering context, or ``None``.

    Returns:
        Rendered chapter Markdown block.
    """
    from mkforge.document import Chapter  # noqa: PLC0415

    typed = cast("Chapter", chapter)
    title = _heading_title(typed.title, context)
    parts = [f"## {title}"]
    _render_children(parts, typed.children, depth=1, context=context)
    return "\n\n".join(parts)


def _render_children(
    parts: list[str],
    children: Sequence[object],
    depth: int,
    context: NumberingContext | None,
) -> None:
    """Append rendered child content to the block list.

    Args:
        parts: Mutable block accumulator.
        children: Child nodes to render.
        depth: One-based section nesting depth below the parent chapter.
        context: Active numbering context, or ``None``.
    """
    _enter_level(context)
    parts.extend(_render_child(child, depth, context) for child in children)
    _leave_level(context)


def _render_child(
    child: object,
    depth: int,
    context: NumberingContext | None,
) -> str:
    """Render one child node.

    Args:
        child: Section or content element to render.
        depth: One-based section nesting depth below the parent chapter.
        context: Active numbering context, or ``None``.

    Returns:
        Rendered Markdown block string.
    """
    from mkforge.document import Section  # noqa: PLC0415

    if isinstance(child, Section):
        return _render_section(child, depth, context)
    return render_content_element(child)


def _render_section(
    section: object,
    depth: int,
    context: NumberingContext | None,
) -> str:
    """Render one section and its children.

    Args:
        section: Section instance.
        depth: One-based nesting depth below the parent chapter.
        context: Active numbering context, or ``None``.

    Returns:
        Rendered section Markdown block.
    """
    from mkforge.document import (  # noqa: PLC0415
        Section,
        compute_section_heading_level,
    )

    typed = cast("Section", section)
    level = compute_section_heading_level(depth)
    title = _heading_title(typed.title, context)
    parts = [f"{'#' * level} {title}"]
    _render_children(parts, typed.children, depth + 1, context)
    return "\n\n".join(parts)


def _heading_title(title: str, context: NumberingContext | None) -> str:
    """Return a heading title, optionally prefixed with a numbering counter.

    Args:
        title: Raw heading title.
        context: Active numbering context, or ``None`` when numbering is off.

    Returns:
        Numbered or plain heading title.
    """
    if context is None:
        return title
    context.advance()
    return _numbered_title(title, context)


def _enter_level(context: NumberingContext | None) -> None:
    """Push a new counter level when numbering is active.

    Args:
        context: Active numbering context, or ``None``.
    """
    if context is not None:
        context.enter_level()


def _leave_level(context: NumberingContext | None) -> None:
    """Pop the current counter level when numbering is active.

    Args:
        context: Active numbering context, or ``None``.
    """
    if context is not None:
        context.leave_level()


# ---------------------------------------------------------------------------
# Input guard
# ---------------------------------------------------------------------------


def _validate_report(report: object) -> None:
    """Validate that the argument is a Report instance.

    Args:
        report: Candidate report.

    Raises:
        TypeError: If the argument is not a ``Report`` instance.
    """
    from mkforge.document import Report  # noqa: PLC0415

    if not isinstance(report, Report):
        message = f"report must be a Report; got {type(report).__name__}."
        raise TypeError(message)
