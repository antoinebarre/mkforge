"""MD012 checks for multiple consecutive blank lines.

This rule belongs to Markdown verification because consecutive blank lines
add visual noise without rendering benefit. It emits one diagnostic for each
blank line that immediately follows another blank line outside fenced code.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for consecutive blank lines outside fenced code.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for multiple consecutive blank lines.
    """
    diagnostics: list[Diagnostic] = []
    previous_blank = False
    for line in lines_outside_fenced_code(source):
        blank = not line.text.strip()
        if blank and previous_blank:
            diagnostics.append(
                _diagnostic(
                    "MD012",
                    line.number,
                    1,
                    "Remove multiple consecutive blank lines.",
                ),
            )
        previous_blank = blank
    return tuple(diagnostics)
