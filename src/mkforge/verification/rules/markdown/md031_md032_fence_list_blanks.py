"""MD031 and MD032 check blank lines around fenced blocks and lists.

These two rules belong together because they both enforce structural
separation via blank lines:
- MD031: fenced code blocks must be surrounded by blank lines.
- MD032: list items must be surrounded by blank lines when adjacent to
  non-list content.
Each rule emits one diagnostic per non-conforming structural element.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _after_blank_diagnostics,
    _before_blank_diagnostics,
    _fenced_blocks,
    _list_items,
    _next_line_is_list_item,
    _previous_line_is_list_item,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD031 and MD032 structural blank-line diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for missing blank lines around fenced blocks and lists.
    """
    return (*_fence_blank_lines(source), *_list_blank_lines(source))


def _fence_blank_lines(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD031 diagnostics for fenced blocks missing surrounding blanks.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each fence opener or closer not surrounded by blank
        lines.
    """
    diagnostics: list[Diagnostic] = []
    for block in _fenced_blocks(source):
        diagnostics.extend(
            _before_blank_diagnostics(
                source.lines,
                block.start,
                "MD031",
                "Add blank lines around fenced code blocks.",
            ),
        )
        diagnostics.extend(
            _after_blank_diagnostics(
                source.lines,
                block.end,
                "MD031",
                "Add blank lines around fenced code blocks.",
            ),
        )
    return tuple(diagnostics)


def _list_blank_lines(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD032 diagnostics for list items missing surrounding blanks.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for list items adjacent to non-list content without a
        blank line separator.
    """
    diagnostics: list[Diagnostic] = []
    items = _list_items(source)
    for item in items:
        previous_is_list = _previous_line_is_list_item(source.lines, item.line)
        next_is_list = _next_line_is_list_item(source.lines, item.line)
        if not previous_is_list:
            diagnostics.extend(
                _before_blank_diagnostics(
                    source.lines,
                    item.line,
                    "MD032",
                    "Add blank lines around lists.",
                ),
            )
        if not next_is_list:
            diagnostics.extend(
                _after_blank_diagnostics(
                    source.lines,
                    item.line,
                    "MD032",
                    "Add blank lines around lists.",
                ),
            )
    return tuple(diagnostics)
