"""Markdown heading numbering helpers."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from mkforge.verification.policy import MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

_ATX_HEADING = re.compile(
    r"^(?P<indent> {0,3})(?P<mark>#{1,6})(?P<gap>[ \t]+|$)(?P<body>.*)$",
)
_HEADING_NUMBERING = re.compile(
    r"^(?:(?:\d+(?:\.\d+)+\.?|\d+[.-]|\d{1,3})(?:\s*-\s*|\s+))"
    r"(?P<title>\S.*)$",
)
_CLOSING_ATX_MARKER = re.compile(
    r"^(?P<title>.*?)(?P<closing>[ \t]+#{1,}[ \t]*)$",
)
_TEXT_TYPE_ERROR = "text must be a string"
_MARKDOWN_TYPE_ERROR = "markdown must be a string"
_SEPARATOR_TYPE_ERROR = "separator must be a string"
_FIRST_NUMBER_TYPE_ERROR = "first_number must be an integer"
_FIRST_NUMBER_VALUE_ERROR = "first_number must be greater than zero"
_START_LEVEL_TYPE_ERROR = "start_level must be an integer"
_START_LEVEL_VALUE_ERROR = "start_level must be between 1 and 6"
_MIN_HEADING_LEVEL = 1
_MAX_HEADING_LEVEL = 6


def strip_heading_numbering_text(text: str) -> str:
    """Remove a leading numeric heading prefix from heading text.

    Args:
        text: Heading text without Markdown heading markers.

    Returns:
        Heading text with one leading numeric prefix removed when present.

    Raises:
        TypeError: If text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(_TEXT_TYPE_ERROR)
    match = _HEADING_NUMBERING.match(text)
    if not match:
        return text
    return match.group("title")


def strip_markdown_heading_numbering(markdown: str) -> str:
    """Remove numeric prefixes from ATX headings outside fenced code.

    Args:
        markdown: Markdown source text.

    Returns:
        Markdown source with ATX heading numbering removed.

    Raises:
        TypeError: If markdown is not a string.
    """
    if not isinstance(markdown, str):
        raise TypeError(_MARKDOWN_TYPE_ERROR)
    return _rewrite_markdown_headings(markdown, _strip_heading_line)


def renumber_markdown_headings(
    markdown: str,
    *,
    separator: str = ". ",
    first_number: int = 1,
    start_level: int = 1,
) -> str:
    """Rewrite ATX headings with hierarchical numeric prefixes.

    Args:
        markdown: Markdown source text.
        separator: Text inserted between each generated number and title.
        first_number: First top-level heading number to generate.
        start_level: First heading level that receives a generated number.

    Returns:
        Markdown source with coherent ATX heading numbering.

    Raises:
        TypeError: If markdown or separator is not a string.
        TypeError: If first_number is not an integer.
        TypeError: If start_level is not an integer.
        ValueError: If first_number is less than one.
        ValueError: If start_level is outside Markdown heading levels.
    """
    if not isinstance(markdown, str):
        raise TypeError(_MARKDOWN_TYPE_ERROR)
    _validate_renumber_options(separator, first_number, start_level)

    counters = [0, 0, 0, 0, 0, 0]

    def renumber(line: str) -> str:
        """Return an ATX heading line with the next hierarchy number.

        Args:
            line: Markdown line outside fenced code.

        Returns:
            Rewritten heading line, or the original line when it is not ATX.
        """
        heading = _parse_atx_heading_line(line)
        if heading is None:
            return line
        title = strip_heading_numbering_text(heading.title)
        if heading.level < start_level:
            return _format_atx_heading_line(heading, title)
        number = _next_heading_number(
            counters,
            heading.level - start_level + 1,
            first_number,
        )
        return _format_atx_heading_line(heading, f"{number}{separator}{title}")

    return _rewrite_markdown_headings(markdown, renumber)


def _validate_renumber_options(
    separator: str,
    first_number: int,
    start_level: int,
) -> None:
    """Validate Markdown heading renumbering options.

    Args:
        separator: Text inserted between each generated number and title.
        first_number: First top-level heading number to generate.
        start_level: First heading level that receives a generated number.

    Raises:
        TypeError: If separator is not a string.
        TypeError: If first_number is not an integer.
        TypeError: If start_level is not an integer.
        ValueError: If first_number is less than one.
        ValueError: If start_level is outside Markdown heading levels.
    """
    if not isinstance(separator, str):
        raise TypeError(_SEPARATOR_TYPE_ERROR)
    if isinstance(first_number, bool) or not isinstance(first_number, int):
        raise TypeError(_FIRST_NUMBER_TYPE_ERROR)
    if isinstance(start_level, bool) or not isinstance(start_level, int):
        raise TypeError(_START_LEVEL_TYPE_ERROR)
    if first_number < 1:
        raise ValueError(_FIRST_NUMBER_VALUE_ERROR)
    if not _MIN_HEADING_LEVEL <= start_level <= _MAX_HEADING_LEVEL:
        raise ValueError(_START_LEVEL_VALUE_ERROR)


def _rewrite_markdown_headings(
    markdown: str,
    replace_line: _HeadingLineRewriter,
) -> str:
    """Rewrite ATX heading lines outside fenced code.

    Args:
        markdown: Markdown source text.
        replace_line: Callable that rewrites one outside-fence line.

    Returns:
        Markdown source after applying the line rewriter.
    """
    source = MarkdownSource.from_text(markdown)
    outside_numbers = {
        line.number for line in lines_outside_fenced_code(source)
    }
    lines = markdown.splitlines(keepends=True)
    return "".join(
        replace_line(line) if number in outside_numbers else line
        for number, line in enumerate(lines, start=1)
    )


def _strip_heading_line(line: str) -> str:
    """Return an ATX heading line with numeric heading text removed.

    Args:
        line: Markdown line outside fenced code.

    Returns:
        Rewritten heading line, or the original line when it is not ATX.
    """
    heading = _parse_atx_heading_line(line)
    if heading is None:
        return line
    title = strip_heading_numbering_text(heading.title)
    return _format_atx_heading_line(heading, title)


def _next_heading_number(
    counters: list[int],
    level: int,
    first_number: int,
) -> str:
    """Return the next hierarchical number for a heading level.

    Args:
        counters: Mutable counters indexed by heading level.
        level: Heading level from 1 to 6.
        first_number: First top-level heading number to generate.

    Returns:
        Dot-separated heading number.
    """
    index = level - 1
    for parent in range(index):
        if counters[parent] == 0:
            counters[parent] = first_number if parent == 0 else 1
    if index == 0 and counters[index] == 0:
        counters[index] = first_number
    else:
        counters[index] += 1
    for child in range(level, len(counters)):
        counters[child] = 0
    return ".".join(str(value) for value in counters[:level])


def _parse_atx_heading_line(line: str) -> _ParsedAtxHeading | None:
    """Return parsed ATX heading parts for one Markdown line.

    Args:
        line: Markdown line, possibly including a line ending.

    Returns:
        Parsed heading parts, or None when the line is not an ATX heading.
    """
    text, ending = _split_line_ending(line)
    match = _ATX_HEADING.match(text)
    if not match:
        return None
    title, closing = _split_closing_marker(match.group("body"))
    return _ParsedAtxHeading(
        indent=match.group("indent"),
        marker=match.group("mark"),
        level=len(match.group("mark")),
        title=title.strip(),
        closing=closing,
        ending=ending,
    )


def _split_line_ending(line: str) -> tuple[str, str]:
    """Split one line into content and newline sequence.

    Args:
        line: Markdown line with or without a line ending.

    Returns:
        Pair containing the line content and original line ending.
    """
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith(("\r", "\n")):
        return line[:-1], line[-1]
    return line, ""


def _split_closing_marker(body: str) -> tuple[str, str]:
    """Split ATX heading body into title text and optional closing marker.

    Args:
        body: Text after the opening ATX marker.

    Returns:
        Pair containing title text and closing marker text.
    """
    stripped = body.rstrip()
    if not stripped.endswith("#"):
        return body, ""
    match = _CLOSING_ATX_MARKER.match(body)
    if not match:
        return body, ""
    return match.group("title"), match.group("closing")


def _format_atx_heading_line(heading: _ParsedAtxHeading, title: str) -> str:
    """Return one ATX heading line from parsed parts and title text.

    Args:
        heading: Parsed ATX heading parts.
        title: Replacement heading title.

    Returns:
        Formatted Markdown heading line.
    """
    return (
        f"{heading.indent}{heading.marker} {title}"
        f"{heading.closing}{heading.ending}"
    )


@dataclass(frozen=True)
class _ParsedAtxHeading:
    """Parsed ATX heading line parts.

    Attributes:
        indent: Leading spaces before the ATX marker.
        marker: Opening ATX marker.
        level: Heading level from 1 to 6.
        title: Heading text without opening or closing markers.
        closing: Optional closing ATX marker including surrounding spacing.
        ending: Original line ending.
    """

    indent: str
    marker: str
    level: int
    title: str
    closing: str
    ending: str


type _HeadingLineRewriter = Callable[[str], str]
