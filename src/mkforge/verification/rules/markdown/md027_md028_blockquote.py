"""MD027 and MD028 check blockquote marker formatting.

These two rules belong together because they both enforce blockquote marker
conventions:
- MD027: only one space is allowed after the ``>`` marker.
- MD028: blank lines inside a blockquote must carry a ``>`` marker.
Each rule emits one diagnostic per non-conforming line.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import _diagnostic
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD027 and MD028 blockquote formatting diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for blockquote marker spacing and blank-line violations.
    """
    return (*_blockquote_spacing(source), *_blockquote_blank_line(source))


def _blockquote_spacing(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD027 diagnostics for blockquote markers with multiple spaces.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for ``> `` markers followed by more than one space.
    """
    return tuple(
        _diagnostic(
            "MD027",
            line.number,
            1,
            "Use one space after the blockquote marker.",
        )
        for line in lines_outside_fenced_code(source)
        if re.match(r"^ *> {2,}\S", line.text)
    )


def _blockquote_blank_line(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD028 diagnostics for bare blank lines inside blockquotes.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for blank lines between blockquote paragraphs that
        lack a ``>`` marker.
    """
    diagnostics: list[Diagnostic] = []
    lines = lines_outside_fenced_code(source)
    for index, line in enumerate(lines[1:-1], start=1):
        if line.text.strip():
            continue
        if lines[index - 1].text.lstrip().startswith(">") and lines[
            index + 1
        ].text.lstrip().startswith(">"):
            diagnostics.append(
                _diagnostic(
                    "MD028",
                    line.number,
                    1,
                    "Keep blockquote markers on blank quote lines.",
                ),
            )
    return tuple(diagnostics)
