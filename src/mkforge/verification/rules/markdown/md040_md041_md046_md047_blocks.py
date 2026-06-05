"""MD040, MD041, MD046, MD047 check code block and document structure.

These four rules belong together because they all enforce document-level
structural conventions:
- MD040: fenced code blocks must specify a language info string.
- MD041: the first line must be a heading of the configured level.
- MD046: all code blocks must use the configured style (fenced or indented).
- MD047: the file must end with exactly one newline character.
Each rule emits one diagnostic per violation.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _code_filtered_lines,
    _diagnostic,
    _fenced_blocks,
    _headings,
    _int_option,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD040, MD041, MD046, and MD047 diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for code block and document structure violations.
    """
    return (
        *_fence_language(source),
        *first_line_heading(source),
        *code_block_style(source),
        *_single_trailing_newline(source),
    )


def _fence_language(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD040 diagnostics for fenced blocks without a language string.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for fenced code blocks missing a language info string.
    """
    return tuple(
        _diagnostic(
            "MD040",
            block.start,
            1,
            "Specify a fenced code block language.",
        )
        for block in _fenced_blocks(source)
        if not block.info.strip()
    )


def first_line_heading(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD041 diagnostics when the first line is not a heading.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostic when the first line is not the configured heading level,
        or an empty tuple when the document is conforming.
    """
    if not source.lines:
        return ()
    expected = _int_option(source, "MD041", "level", 1)
    headings = _headings(source)
    if (
        headings
        and headings[0].line == source.lines[0].number
        and headings[0].level == expected
    ):
        return ()
    return (
        _diagnostic(
            "MD041",
            1,
            1,
            f"Start files with a level {expected} heading.",
        ),
    )


def code_block_style(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD046 diagnostics for code blocks using the wrong style.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for code blocks that do not match the configured style
        (``fenced`` or ``indented``). Returns empty tuple for ``consistent``.
    """
    style = str(source.rule_options("MD046").get("style", "fenced"))
    if style == "consistent":
        return ()
    if style == "fenced":
        return tuple(
            _diagnostic("MD046", line.number, 1, "Use fenced code blocks.")
            for line in _code_filtered_lines(
                source,
                "MD046",
                "ignore_code_blocks",
            )
            if line.text.startswith("    ")
        )
    return tuple(
        _diagnostic("MD046", block.start, 1, "Use indented code blocks.")
        for block in _fenced_blocks(source)
    )


def _single_trailing_newline(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD047 diagnostics when the file does not end with one newline.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostic when the file is missing a trailing newline or has
        multiple trailing newlines, or an empty tuple when conforming.
    """
    if source.text.endswith("\n") and not source.text.endswith("\n\n"):
        return ()
    line = len(source.lines) if source.lines else 1
    return (_diagnostic("MD047", line, 1, "End files with a single newline."),)
