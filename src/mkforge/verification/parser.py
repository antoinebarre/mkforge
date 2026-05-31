"""Small Markdown parser for verification and validation."""

from __future__ import annotations

from collections.abc import Mapping

from mkforge.diagnostics import Line, RuleConfig, SourceContext
from mkforge.verification.heading_parser import parse_headings
from mkforge.verification.patterns import FENCE_RE


def parse_markdown(
    source: str,
    config: Mapping[str, RuleConfig] | None = None,
) -> SourceContext:
    """Parse Markdown into a diagnostic source context.

    Args:
        source: Markdown source text.
        config: Optional per-rule configuration mapping.

    Returns:
        Parsed source context.
    """
    raw_lines = source.splitlines()
    if source.endswith("\n"):
        raw_lines = source[:-1].splitlines()
    lines = _parse_lines(raw_lines)
    return SourceContext(source, lines, parse_headings(lines), config or {})


def _parse_lines(raw_lines: list[str]) -> tuple[Line, ...]:
    """Parse line state for fenced code blocks.

    Args:
        raw_lines: Raw Markdown source lines.

    Returns:
        Parse line state for fenced code blocks.
    """
    parsed: list[Line] = []
    in_code = False
    fence = ""
    for index, text in enumerate(raw_lines, start=1):
        parsed.append(Line(index, text, in_code))
        in_code, fence = _next_fence_state(text, in_code=in_code, fence=fence)
    return tuple(parsed)


def _next_fence_state(
    text: str,
    *,
    in_code: bool,
    fence: str,
) -> tuple[bool, str]:
    """Return updated fenced-code parsing state.

    Args:
        text: Source line text.
        in_code: Whether the line is inside a fenced code block.
        fence: Current fenced-code marker.

    Returns:
        Updated fenced-code parsing state.
    """
    match = FENCE_RE.match(text)
    if match is None:
        return in_code, fence
    if not in_code:
        return True, match.group(1)[0]
    return (False, "") if match.group(1).startswith(fence) else (True, fence)
