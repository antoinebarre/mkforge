"""MD004 checks that unordered list markers are consistent.

This rule belongs to Markdown verification because mixing bullet characters
(*,  +, -) reduces document consistency. It emits one diagnostic for each
unordered list item whose marker differs from the configured or detected
expectation.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _expected_unordered_mark,
    _mark_name,
    _unordered_items,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for unordered list items with inconsistent markers.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for list items that use an unexpected bullet character.
    """
    style = str(source.rule_options("MD004").get("style", "consistent"))
    items = tuple(_unordered_items(source))
    if not items:
        return ()
    expected = _expected_unordered_mark(style, items)
    return tuple(
        _diagnostic(
            "MD004",
            item.line,
            len(item.indent) + 1,
            f"Use {expected} unordered list markers.",
        )
        for item in items
        if expected and _mark_name(item.marker) != expected
    )
