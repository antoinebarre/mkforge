"""GFM003 checks GitHub Flavored Markdown task list markers.

This rule belongs to GFM verification because task list item markers are valid
only when the bracket contains a space or `x`. It emits one diagnostic for each
list item that uses a malformed task marker.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import Diagnostic, MarkdownSource

RULE_ID = "GFM003"
NAME = "GFM task list marker"
TASK_MARKER = re.compile(r"^ {0,3}(?:[-+*]|\d+[.)])\s+\[([^ xX])\]")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for malformed GFM task list item markers.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for malformed task markers.
    """
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        match = TASK_MARKER.search(line.text)
        if match:
            diagnostics.append(_diagnostic(line.number, match.start(1)))
    return tuple(diagnostics)


def _diagnostic(line: int, zero_based_column: int) -> Diagnostic:
    """Return a task-list marker diagnostic.

    Args:
        line: One-based source line number.
        zero_based_column: Zero-based column where the marker content starts.

    Returns:
        Task-list marker diagnostic.
    """
    return Diagnostic(
        rule_id=RULE_ID,
        name=NAME,
        line=line,
        column=zero_based_column + 1,
        message="Use a space or x inside GFM task list item brackets.",
    )
