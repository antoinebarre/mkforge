"""Small Markdown parser helpers for linting."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_api import MarkdownLine, MarkdownLintContext
from mkforge.markdown_lint_heading_parser import parse_headings
from mkforge.markdown_lint_parser_patterns import FENCE_RE

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mkforge.markdown_lint_api import RuleConfig


def parse_markdown(
    source: str,
    config: Mapping[str, RuleConfig] | None = None,
) -> MarkdownLintContext:
    """Parse Markdown text into a lint context.

    Args:
        source: Markdown source.
        config: Optional rule configuration.

    Returns:
        Parsed lint context.
    """
    raw_lines = source.splitlines()
    if source.endswith("\n"):
        raw_lines = source[:-1].splitlines()
    lines = _parse_lines(raw_lines)
    headings = parse_headings(lines)
    return MarkdownLintContext(source, lines, headings, config or {})


def _parse_lines(raw_lines: list[str]) -> tuple[MarkdownLine, ...]:
    """Parse line state for fenced code blocks."""
    parsed: list[MarkdownLine] = []
    in_code = False
    fence = ""
    for index, text in enumerate(raw_lines, start=1):
        parsed.append(MarkdownLine(index, text, in_code))
        in_code, fence = _next_fence_state(text, in_code=in_code, fence=fence)
    return tuple(parsed)


def _next_fence_state(
    text: str,
    *,
    in_code: bool,
    fence: str,
) -> tuple[bool, str]:
    """Return updated fenced-code parsing state."""
    match = FENCE_RE.match(text)
    if match is None:
        return in_code, fence
    if not in_code:
        return True, match.group(1)[0]
    return _close_fence(match.group(1), fence)


def _close_fence(marker: str, fence: str) -> tuple[bool, str]:
    """Return state after a possible closing fence marker."""
    return (False, "") if marker.startswith(fence) else (True, fence)
