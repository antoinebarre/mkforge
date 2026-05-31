"""Setext heading parser helpers for Markdown linting."""

from __future__ import annotations

from mkforge.markdown_lint_api import MarkdownHeading, MarkdownLine

SETEXT_H2_MIN_LENGTH = 3


def setext_heading(
    lines: tuple[MarkdownLine, ...],
    index: int,
) -> MarkdownHeading | None:
    """Parse one setext heading."""
    if not _can_parse_setext(lines, index):
        return None
    previous = lines[index - 1]
    level = _setext_level(lines[index].text.strip())
    if level is None:
        return None
    return MarkdownHeading(
        previous.number,
        level,
        previous.text.strip(),
        "setext",
    )


def _setext_level(marker: str) -> int | None:
    """Return setext heading level for a marker line."""
    if set(marker) == {"="}:
        return 1
    if _is_setext_h2(marker):
        return 2
    return None


def _is_setext_h2(marker: str) -> bool:
    """Return whether a marker line is a level-2 setext marker."""
    return set(marker) == {"-"} and len(marker) >= SETEXT_H2_MIN_LENGTH


def _can_parse_setext(lines: tuple[MarkdownLine, ...], index: int) -> bool:
    """Return whether a line can be interpreted as a setext marker."""
    if index == 0 or lines[index].in_code:
        return False
    previous = lines[index - 1]
    return bool(previous.text.strip()) and not previous.in_code
