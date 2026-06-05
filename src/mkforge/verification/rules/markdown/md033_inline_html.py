"""MD033 checks for inline HTML elements in Markdown source.

This rule belongs to Markdown verification because inline HTML breaks
portability across Markdown renderers. It emits one diagnostic per HTML
tag found outside fenced code that is not in the configured allowed list.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    HTML_TAG,
    _allowed_html,
    _diagnostic,
)
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for inline HTML tags not in the allowed list.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each disallowed inline HTML tag.
    """
    allowed = _allowed_html(source)
    diagnostics: list[Diagnostic] = []
    for line in lines_outside_fenced_code(source):
        diagnostics.extend(
            _diagnostic(
                "MD033",
                line.number,
                match.start() + 1,
                "Avoid inline HTML.",
            )
            for match in HTML_TAG.finditer(line.text)
            if match.group(1).lower() not in allowed
        )
    return tuple(diagnostics)
