"""Diagnostic helper functions for repeated Markdown rule scans."""

from __future__ import annotations

import re
from collections.abc import Iterable

from mkforge.verification.policy import Diagnostic, MarkdownLine


def matching_lines(
    *,
    lines: Iterable[MarkdownLine],
    pattern: re.Pattern[str],
    rule_id: str,
    name: str,
    message: str,
) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines matching a regular expression.

    Args:
        lines: Source lines to scan.
        pattern: Compiled regular expression.
        rule_id: Stable conformance rule identifier.
        name: Human-readable rule name.
        message: Diagnostic message.

    Returns:
        Diagnostics for matching lines.
    """
    return tuple(
        Diagnostic(
            rule_id=rule_id,
            name=name,
            line=line.number,
            column=match.start() + 1,
            message=message,
        )
        for line in lines
        if (match := pattern.search(line.text))
    )
