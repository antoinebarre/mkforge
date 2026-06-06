"""Shared helpers for Markdown conformance rule modules.

This module provides parsed document model types (_Heading, _ListItem,
_CodeBlock), document scanning functions, and diagnostic construction
helpers reused across individual rule modules. It emits no diagnostics
itself; rules import only the helpers they need.
"""

from __future__ import annotations

import re

from mkforge.verification.policy import (
    Diagnostic,
    MarkdownLine,
    MarkdownSource,
)
from mkforge.verification.source_scan import lines_outside_fenced_code

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

ATX_HEADING = re.compile(r"^(?P<indent> *)(?P<mark>#{1,6})(?P<body>.*)$")
SETEXT_MARKER = re.compile(r"^ {0,3}(=+|-+)\s*$")
LIST_ITEM = re.compile(
    r"^(?P<indent> *)(?P<mark>(?:[-+*])|(?:\d+[.)]))(?P<gap> +)",
)
UNORDERED_ITEM = re.compile(r"^(?P<indent> *)(?P<mark>[-+*])(?P<gap> +)")
ORDERED_ITEM = re.compile(
    r"^(?P<indent> *)(?P<number>\d+)(?P<delim>[.)])(?P<gap> +)",
)
FENCE_LINE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
HTML_TAG = re.compile(r"</?([A-Za-z][A-Za-z0-9-]*)(?:\s|/?>)")
HORIZONTAL_RULE = re.compile(r"^ {0,3}[-*_][ \-*_]*\s*$")
EMPHASIS_ONLY = re.compile(
    r"^\s*(?:\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_)\s*$",
)
SETEXT_WITH_ATX_MIN_LEVEL = 3

RULE_NAMES = {
    "MD001": "Heading increment",
    "MD002": "First heading level",
    "MD003": "Heading style",
    "MD004": "Unordered list style",
    "MD005": "List indentation consistency",
    "MD006": "Top-level unordered list indentation",
    "MD007": "Unordered list indentation",
    "MD009": "Trailing spaces",
    "MD010": "Hard tabs",
    "MD012": "Multiple blank lines",
    "MD013": "Line length",
    "MD014": "Command prompt without output",
    "MD019": "ATX heading multiple spaces",
    "MD021": "Closed ATX heading multiple spaces",
    "MD022": "Heading blank lines",
    "MD023": "Heading start left",
    "MD024": "Duplicate heading",
    "MD025": "Multiple top-level headings",
    "MD026": "Heading trailing punctuation",
    "MD027": "Blockquote marker spacing",
    "MD028": "Blank line inside blockquote",
    "MD029": "Ordered list prefix",
    "MD030": "List marker spacing",
    "MD031": "Fence blank lines",
    "MD032": "List blank lines",
    "MD033": "Inline HTML",
    "MD035": "Horizontal rule style",
    "MD036": "Emphasis used as heading",
    "MD040": "Fence language",
    "MD041": "First line heading",
    "MD046": "Code block style",
    "MD047": "Single trailing newline",
}


# ---------------------------------------------------------------------------
# Document model types
# ---------------------------------------------------------------------------


class _Heading:
    """Parsed Markdown heading.

    Attributes:
        line: One-based line number of the heading.
        level: Heading level (1-6).
        text: Heading text without markers.
        style: Heading style: ``atx``, ``atx_closed``, or ``setext``.
    """

    def __init__(self, line: int, level: int, text: str, style: str) -> None:
        """Create a parsed heading.

        Args:
            line: One-based line number.
            level: Heading level (1-6).
            text: Heading text without markers.
            style: Heading style identifier.
        """
        self.line = line
        self.level = level
        self.text = text
        self.style = style


class _ListItem:
    """Parsed Markdown list item.

    Attributes:
        line: One-based line number of the item.
        indent: Leading whitespace string.
        marker: List marker text (e.g. ``-``, ``1.``).
        gap: Number of spaces after the marker.
        ordered: True when the item belongs to an ordered list.
    """

    def __init__(self, line: int, indent: str, marker: str, gap: int) -> None:
        """Create a parsed list item.

        Args:
            line: One-based line number.
            indent: Leading whitespace.
            marker: List marker text.
            gap: Spaces after the marker.
        """
        self.line = line
        self.indent = indent
        self.marker = marker
        self.gap = gap
        self.ordered = marker[0].isdigit()


class _CodeBlock:
    """Parsed fenced code block.

    Attributes:
        start: One-based line number of the opening fence.
        end: One-based line number of the closing fence.
        info: Info string after the opening fence marker.
        lines: Content lines between the fences.
    """

    def __init__(
        self,
        start: int,
        end: int,
        info: str,
        lines: tuple[MarkdownLine, ...],
    ) -> None:
        """Create a parsed code block.

        Args:
            start: One-based opening fence line number.
            end: One-based closing fence line number.
            info: Info string after the opening fence.
            lines: Content lines inside the block.
        """
        self.start = start
        self.end = end
        self.info = info
        self.lines = lines


# ---------------------------------------------------------------------------
# Document scanning helpers
# ---------------------------------------------------------------------------


def _headings(source: MarkdownSource) -> tuple[_Heading, ...]:
    """Return parsed headings outside fenced code.

    Args:
        source: Markdown source context.

    Returns:
        Parsed headings in document order.
    """
    lines = lines_outside_fenced_code(source)
    headings: list[_Heading] = []
    for index, line in enumerate(lines):
        match = ATX_HEADING.match(line.text)
        if match and match.group("mark").strip("#") == "":
            headings.append(_atx_heading(line, match))
            continue
        if (
            index > 0
            and SETEXT_MARKER.match(line.text)
            and lines[index - 1].text.strip()
        ):
            level = 1 if line.text.strip().startswith("=") else 2
            headings.append(
                _Heading(
                    lines[index - 1].number,
                    level,
                    lines[index - 1].text.strip(),
                    "setext",
                ),
            )
    return tuple(headings)


def _atx_heading(line: MarkdownLine, match: re.Match[str]) -> _Heading:
    """Return one parsed ATX heading.

    Args:
        line: Source line containing the heading.
        match: Regex match from ATX_HEADING pattern.

    Returns:
        Parsed ATX heading.
    """
    body = match.group("body").strip()
    style = "atx"
    if body.endswith("#") and " #" in body:
        style = "atx_closed"
        body = body.rstrip("#").strip()
    return _Heading(line.number, len(match.group("mark")), body, style)


def _list_items(source: MarkdownSource) -> tuple[_ListItem, ...]:
    """Return parsed list items outside fenced code.

    Args:
        source: Markdown source context.

    Returns:
        Parsed list items in document order.
    """
    items: list[_ListItem] = []
    for line in lines_outside_fenced_code(source):
        match = LIST_ITEM.match(line.text)
        if match:
            items.append(
                _ListItem(
                    line.number,
                    match.group("indent"),
                    match.group("mark"),
                    len(match.group("gap")),
                ),
            )
    return tuple(items)


def _unordered_items(source: MarkdownSource) -> tuple[_ListItem, ...]:
    """Return unordered list items outside fenced code.

    Args:
        source: Markdown source context.

    Returns:
        Parsed unordered list items.
    """
    return tuple(item for item in _list_items(source) if not item.ordered)


def _ordered_items(source: MarkdownSource) -> tuple[_ListItem, ...]:
    """Return ordered list items outside fenced code.

    Args:
        source: Markdown source context.

    Returns:
        Parsed ordered list items.
    """
    return tuple(item for item in _list_items(source) if item.ordered)


def _fenced_blocks(source: MarkdownSource) -> tuple[_CodeBlock, ...]:
    """Return parsed fenced code blocks.

    Args:
        source: Markdown source context.

    Returns:
        Parsed fenced code blocks in document order.
    """
    blocks: list[_CodeBlock] = []
    start = 0
    info = ""
    marker = ""
    lines: list[MarkdownLine] = []
    for line in source.lines:
        match = FENCE_LINE.match(line.text)
        if marker:
            if match and match.group("fence").startswith(marker):
                blocks.append(
                    _CodeBlock(start, line.number, info, tuple(lines)),
                )
                marker = ""
                lines = []
            else:
                lines.append(line)
            continue
        if match:
            marker = match.group("fence")[:3]
            start = line.number
            info = match.group("info")
    return tuple(blocks)


# ---------------------------------------------------------------------------
# Rule option helpers
# ---------------------------------------------------------------------------


def _int_option(
    source: MarkdownSource,
    rule_id: str,
    key: str,
    default: int,
) -> int:
    """Return an integer rule option, falling back to the default.

    Args:
        source: Markdown source context.
        rule_id: Rule identifier to read.
        key: Option key name.
        default: Default value when option is absent or wrong type.

    Returns:
        Integer option value.
    """
    value = source.rule_options(rule_id).get(key, default)
    return value if isinstance(value, int) else default


def _code_filtered_lines(
    source: MarkdownSource,
    rule_id: str,
    option: str,
) -> tuple[MarkdownLine, ...]:
    """Return lines after applying a code-block ignore option.

    Args:
        source: Markdown source context.
        rule_id: Rule identifier whose option controls filtering.
        option: Option key that enables fenced-code filtering when True.

    Returns:
        Lines outside fenced code when the option is True, all lines otherwise.
    """
    if bool(source.rule_options(rule_id).get(option, False)):
        return lines_outside_fenced_code(source)
    return source.lines


def _line_is_too_long(
    source: MarkdownSource,
    line: MarkdownLine,
    limit: int,
) -> bool:
    """Return whether one line exceeds MD013 length settings.

    Args:
        source: Markdown source context.
        line: Line to check.
        limit: Maximum allowed character count.

    Returns:
        True when the line exceeds the limit after applying table and heading
        exemptions.
    """
    if len(line.text) <= limit:
        return False
    if (
        not bool(source.rule_options("MD013").get("tables", True))
        and "|" in line.text
    ):
        return False
    if not bool(
        source.rule_options("MD013").get("headings", True),
    ) and ATX_HEADING.match(line.text):
        return False
    return " " in line.text[limit:]


# ---------------------------------------------------------------------------
# Heading style helpers
# ---------------------------------------------------------------------------


def _expected_heading_style(style: str, headings: tuple[_Heading, ...]) -> str:
    """Return the expected heading style from configuration or first heading.

    Args:
        style: Configured style or ``consistent``.
        headings: Parsed headings in document order.

    Returns:
        Expected heading style string.
    """
    if style == "consistent" and headings:
        return headings[0].style
    return style


def _heading_style_matches(actual: str, level: int, expected: str) -> bool:
    """Return whether a heading style matches the configured expectation.

    Args:
        actual: Actual heading style.
        level: Heading level (1-6).
        expected: Expected heading style or ``setext_with_atx``.

    Returns:
        True when actual matches expected under the given policy.
    """
    if expected == "setext_with_atx":
        return actual == "setext" or (
            level >= SETEXT_WITH_ATX_MIN_LEVEL and actual == "atx"
        )
    return actual == expected


# ---------------------------------------------------------------------------
# List helpers
# ---------------------------------------------------------------------------


def _expected_unordered_mark(style: str, items: tuple[_ListItem, ...]) -> str:
    """Return the expected unordered list marker name.

    Args:
        style: Configured style or ``consistent``.
        items: Parsed unordered list items.

    Returns:
        Expected marker name (``asterisk``, ``plus``, ``dash``) or empty
        string when the style is unknown.
    """
    if style == "consistent":
        return _mark_name(items[0].marker) if items else ""
    if style in {"asterisk", "plus", "dash"}:
        return style
    return ""


def _mark_name(marker: str) -> str:
    """Return the markdownlint unordered marker name for a marker character.

    Args:
        marker: Marker character (``*``, ``+``, or ``-``).

    Returns:
        Human-readable marker name.
    """
    return {"*": "asterisk", "+": "plus", "-": "dash"}.get(marker, marker)


# ---------------------------------------------------------------------------
# Blank-line diagnostics helpers
# ---------------------------------------------------------------------------


def _blank_line_diagnostics(
    lines: tuple[MarkdownLine, ...],
    number: int,
    rule_id: str,
    message: str,
) -> tuple[Diagnostic, ...]:
    """Return diagnostics when a line lacks surrounding blank lines.

    Args:
        lines: Source lines tuple.
        number: One-based line number to check surroundings of.
        rule_id: Rule identifier for emitted diagnostics.
        message: Diagnostic message.

    Returns:
        Diagnostics for missing blank lines before and after the line.
    """
    return (
        *_before_blank_diagnostics(lines, number, rule_id, message),
        *_after_blank_diagnostics(lines, number, rule_id, message),
    )


def _before_blank_diagnostics(
    lines: tuple[MarkdownLine, ...],
    number: int,
    rule_id: str,
    message: str,
) -> tuple[Diagnostic, ...]:
    """Return a diagnostic when a line lacks a blank line before it.

    Args:
        lines: Source lines tuple.
        number: One-based line number to check.
        rule_id: Rule identifier for the emitted diagnostic.
        message: Diagnostic message.

    Returns:
        Diagnostic tuple with one entry when the preceding line is non-blank.
    """
    index = number - 1
    if index > 0 and lines[index - 1].text.strip():
        return (_diagnostic(rule_id, number, 1, message),)
    return ()


def _after_blank_diagnostics(
    lines: tuple[MarkdownLine, ...],
    number: int,
    rule_id: str,
    message: str,
) -> tuple[Diagnostic, ...]:
    """Return a diagnostic when a line lacks a blank line after it.

    Args:
        lines: Source lines tuple.
        number: One-based line number to check.
        rule_id: Rule identifier for the emitted diagnostic.
        message: Diagnostic message.

    Returns:
        Diagnostic tuple with one entry when the following line is non-blank.
    """
    index = number - 1
    if index + 1 < len(lines) and lines[index + 1].text.strip():
        return (_diagnostic(rule_id, number, 1, message),)
    return ()


def _previous_line_is_list_item(
    lines: tuple[MarkdownLine, ...],
    number: int,
) -> bool:
    """Return whether the previous line is part of the same list.

    Args:
        lines: Source lines tuple.
        number: One-based line number.

    Returns:
        True when the preceding line matches the list item pattern.
    """
    if number <= 1:
        return False
    return LIST_ITEM.match(lines[number - 2].text) is not None


def _next_line_is_list_item(
    lines: tuple[MarkdownLine, ...],
    number: int,
) -> bool:
    """Return whether the next line is part of the same list.

    Args:
        lines: Source lines tuple.
        number: One-based line number.

    Returns:
        True when the following line matches the list item pattern.
    """
    if number >= len(lines):
        return False
    return LIST_ITEM.match(lines[number].text) is not None


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def _allowed_html(source: MarkdownSource) -> set[str]:
    """Return the set of allowed MD033 HTML element names.

    Args:
        source: Markdown source context.

    Returns:
        Lower-case element names allowed by the MD033 configuration.
    """
    raw = str(source.rule_options("MD033").get("allowed_elements", ""))
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


# ---------------------------------------------------------------------------
# Diagnostic factory
# ---------------------------------------------------------------------------


def _diagnostic(
    rule_id: str,
    line: int,
    column: int,
    message: str,
) -> Diagnostic:
    """Return a markdownlint-compatible diagnostic.

    Args:
        rule_id: Stable rule identifier from RULE_NAMES.
        line: One-based line number.
        column: One-based column number.
        message: Precise diagnostic message.

    Returns:
        Diagnostic with category and severity defaults.
    """
    return Diagnostic(
        rule_id=rule_id,
        name=RULE_NAMES[rule_id],
        line=line,
        column=column,
        message=message,
    )
