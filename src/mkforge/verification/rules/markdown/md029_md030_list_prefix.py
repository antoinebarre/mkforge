"""MD029 and MD030 check list item numbering and marker spacing.

These two rules belong together because they both enforce list item marker
conventions:
- MD029: ordered list items must use the configured numbering style.
- MD030: list markers must be followed by exactly the configured number of
  spaces.
Each rule emits one diagnostic per non-conforming list item.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _int_option,
    _list_items,
    _ordered_items,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD029 and MD030 list marker diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for ordered list prefix and list marker spacing violations.
    """
    return (*_ordered_list_prefix(source), *_list_marker_spacing(source))


def _ordered_list_prefix(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD029 diagnostics for non-conforming ordered list prefixes.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for ordered items whose number differs from the configured
        style (``one`` or ``ordered``).
    """
    style = str(source.rule_options("MD029").get("style", "one"))
    expected = 1
    diagnostics: list[Diagnostic] = []
    for item in _ordered_items(source):
        number = int(item.marker.rstrip(".)"))
        valid = number == (expected if style == "ordered" else 1)
        if not valid:
            diagnostics.append(
                _diagnostic(
                    "MD029",
                    item.line,
                    len(item.indent) + 1,
                    "Use the configured ordered list prefix.",
                ),
            )
        expected += 1
    return tuple(diagnostics)


def _list_marker_spacing(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD030 diagnostics for incorrect spacing after list markers.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for list items whose marker gap differs from the
        configured expected space count.
    """
    diagnostics: list[Diagnostic] = []
    for item in _list_items(source):
        rule_id = "MD030"
        key = "ol_single" if item.ordered else "ul_single"
        expected = _int_option(source, rule_id, key, 1)
        if item.gap != expected:
            diagnostics.append(
                _diagnostic(
                    rule_id,
                    item.line,
                    len(item.indent) + len(item.marker) + 1,
                    f"Use {expected} spaces after list markers.",
                ),
            )
    return tuple(diagnostics)
