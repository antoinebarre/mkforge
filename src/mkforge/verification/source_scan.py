"""Source scanning helpers for Markdown conformance rules."""

from __future__ import annotations

import re

from mkforge.verification.policy import MarkdownLine, MarkdownSource

FENCE_START = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def lines_outside_fenced_code(
    source: MarkdownSource,
) -> tuple[MarkdownLine, ...]:
    """Return lines that are not inside fenced code blocks.

    Args:
        source: Markdown source context.

    Returns:
        Lines outside fenced code blocks, including the fence marker lines.
    """
    outside_lines: list[MarkdownLine] = []
    fence_marker = ""
    for line in source.lines:
        marker = _fence_marker(line.text)
        if fence_marker:
            if marker and marker.startswith(fence_marker):
                fence_marker = ""
            continue
        outside_lines.append(line)
        if marker:
            fence_marker = marker[:3]
    return tuple(outside_lines)


def _fence_marker(text: str) -> str:
    """Return the opening fence marker for a line, if any.

    Args:
        text: Source line text.

    Returns:
        Fence marker text or an empty string.
    """
    match = FENCE_START.match(text)
    if not match:
        return ""
    return match.group(1)
