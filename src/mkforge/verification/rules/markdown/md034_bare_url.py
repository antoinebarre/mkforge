"""MD034 checks bare URLs outside GFM autolink syntax.

This rule belongs to Markdown verification because a bare URL is not portable
classic Markdown link syntax. It emits a diagnostic for URL text that is not
wrapped in angle brackets, code spans, or Markdown link syntax.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import (
    Diagnostic,
    MarkdownLine,
    MarkdownSource,
)
from mkforge.verification.source_scan import lines_outside_fenced_code

RULE_ID = "MD034"
NAME = "Bare URL"
BARE_URL = re.compile(r"https?://[^\s<>)]+")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for bare URLs.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for bare URLs.
    """
    diagnostics: list[Diagnostic] = []
    for line in lines_outside_fenced_code(source):
        diagnostics.extend(_line_diagnostics(line))
    return tuple(diagnostics)


def _line_diagnostics(line: MarkdownLine) -> tuple[Diagnostic, ...]:
    """Return bare URL diagnostics for one source line.

    Args:
        line: Source line to scan.

    Returns:
        Diagnostics for bare URLs on the line.
    """
    return tuple(
        Diagnostic(
            rule_id=RULE_ID,
            name=NAME,
            line=line.number,
            column=match.start() + 1,
            message="Wrap bare URLs in angle brackets or Markdown links.",
        )
        for match in BARE_URL.finditer(line.text)
        if not _is_wrapped_url(line.text, match.start(), match.end())
    )


def _is_wrapped_url(text: str, start: int, end: int) -> bool:
    """Return whether a URL is already wrapped by Markdown syntax.

    Args:
        text: Source line text.
        start: Zero-based URL start column.
        end: Zero-based exclusive URL end column.

    Returns:
        True when the URL is enclosed in angle brackets, code, or link syntax.
    """
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return (
        (before == "<" and after == ">")
        or (before == "`" and after == "`")
        or before == "("
    )
