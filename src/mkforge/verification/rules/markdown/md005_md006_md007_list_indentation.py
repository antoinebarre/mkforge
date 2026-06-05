"""MD005, MD006, MD007 check list indentation conformance.

These three rules belong together because they share list item parsing and
all enforce consistent indentation:
- MD005: list items at the same level must use the same indentation.
- MD006: top-level unordered list items must start at column 1.
- MD007: unordered sub-list items must be indented by the configured amount.
Each rule emits one diagnostic per non-conforming list item.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _int_option,
    _list_items,
    _unordered_items,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD005, MD006, and MD007 list indentation diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for list indentation violations.
    """
    return (
        *_list_indentation(source),
        *_top_level_unordered_left(source),
        *_unordered_list_indent(source),
    )


def _list_indentation(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD005 diagnostics for inconsistent list indentation.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for list items whose indentation differs from
        a previously seen item at the same nesting level.
    """
    seen: dict[int, int] = {}
    diagnostics: list[Diagnostic] = []
    for item in _list_items(source):
        level = len(item.indent) // max(
            1,
            _int_option(source, "MD007", "indent", 3),
        )
        indent = len(item.indent)
        if level in seen and seen[level] != indent:
            diagnostics.append(
                _diagnostic(
                    "MD005",
                    item.line,
                    1,
                    "Use consistent indentation for list items.",
                ),
            )
        seen.setdefault(level, indent)
    return tuple(diagnostics)


def _top_level_unordered_left(
    source: MarkdownSource,
) -> tuple[Diagnostic, ...]:
    """Return MD006 diagnostics for indented top-level unordered items.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for top-level unordered items not at column 1.
    """
    return tuple(
        _diagnostic(
            "MD006",
            item.line,
            1,
            "Start top-level unordered lists at the beginning of the line.",
        )
        for item in _unordered_items(source)
        if item.indent
    )


def _unordered_list_indent(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD007 diagnostics for unordered sub-list indentation.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for sub-list items whose indentation is not a multiple
        of the configured indent size.
    """
    expected = _int_option(source, "MD007", "indent", 3)
    return tuple(
        _diagnostic(
            "MD007",
            item.line,
            1,
            f"Indent unordered sublists by {expected} spaces.",
        )
        for item in _unordered_items(source)
        if item.indent and len(item.indent) % expected != 0
    )
