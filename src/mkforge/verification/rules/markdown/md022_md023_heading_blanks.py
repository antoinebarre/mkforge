"""MD022 and MD023 check heading surrounding whitespace and alignment.

These two rules belong together because they both validate the structural
context of headings:
- MD022: every heading must be surrounded by blank lines.
- MD023: every heading must start at column 1.
Each rule emits one diagnostic per non-conforming heading.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic, _headings
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD022 and MD023 heading context diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for heading blank-line and alignment violations.
    """
    return (*_heading_blank_lines(source), *_heading_start_left(source))


def _heading_blank_lines(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD022 diagnostics for headings missing surrounding blank lines.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for headings not surrounded by blank lines.
    """
    diagnostics: list[Diagnostic] = []
    lines = source.lines
    heading_lines = {heading.line for heading in _headings(source)}
    for index, line in enumerate(lines):
        if line.number not in heading_lines:
            continue
        if index > 0 and lines[index - 1].text.strip():
            diagnostics.append(
                _diagnostic(
                    "MD022",
                    line.number,
                    1,
                    "Add a blank line before headings.",
                ),
            )
        if index + 1 < len(lines) and lines[index + 1].text.strip():
            diagnostics.append(
                _diagnostic(
                    "MD022",
                    line.number,
                    1,
                    "Add a blank line after headings.",
                ),
            )
    return tuple(diagnostics)


def _heading_start_left(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD023 diagnostics for indented headings.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for headings that do not start at column 1.
    """
    return tuple(
        _diagnostic(
            "MD023",
            line.number,
            1,
            "Start headings at the beginning of the line.",
        )
        for line in lines_outside_fenced_code(source)
        if re.match(r"^ +#{1,6}\s+", line.text)
    )
