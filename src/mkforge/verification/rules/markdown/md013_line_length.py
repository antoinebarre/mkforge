"""MD013 checks that lines do not exceed the configured maximum length.

This rule belongs to Markdown verification because long lines reduce
readability in editors and diff views. It emits one diagnostic per line
that exceeds the configured limit, with optional exemptions for tables,
headings, and fenced code blocks.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _code_filtered_lines,
    _diagnostic,
    _int_option,
    _line_is_too_long,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines exceeding the configured length limit.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for over-length lines.
    """
    limit = _int_option(source, "MD013", "line_length", 80)
    lines = _code_filtered_lines(source, "MD013", "ignore_code_blocks")
    return tuple(
        _diagnostic(
            "MD013",
            line.number,
            limit + 1,
            f"Line length exceeds {limit} characters.",
        )
        for line in lines
        if _line_is_too_long(source, line, limit)
    )
