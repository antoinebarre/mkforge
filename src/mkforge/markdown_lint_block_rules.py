"""Block-oriented Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import (
    diagnostic,
    is_blank,
    is_fence,
    is_list_item,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLine,
        MarkdownLintContext,
    )


def rule_md014(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report shell prompts in command-only code blocks."""
    return tuple(
        diagnostic(
            "MD014",
            "Commands show output",
            line.number,
            "Omit shell prompt from command-only blocks.",
        )
        for line in context.lines
        if line.in_code and line.text.startswith("$ ")
    )


def rule_md028(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report blank lines inside adjacent blockquotes."""
    diagnostics: list[MarkdownDiagnostic] = []
    for index, line in enumerate(context.lines[1:-1], start=1):
        if _is_blank_between_quotes(context, index, line.text):
            diagnostics.append(
                diagnostic(
                    "MD028",
                    "Blank line in blockquote",
                    line.number,
                    "Use > on blank quote lines.",
                ),
            )
    return tuple(diagnostics)


def rule_md031(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report fences not surrounded by blank lines."""
    return _blank_around("MD031", "Blanks around fences", context, is_fence)


def rule_md032(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report lists not surrounded by blank lines."""
    return _blank_around("MD032", "Blanks around lists", context, is_list_item)


def _is_blank_between_quotes(
    context: MarkdownLintContext,
    index: int,
    text: str,
) -> bool:
    """Return whether a blank line separates adjacent blockquote lines."""
    return (
        is_blank(text)
        and context.lines[index - 1].text.startswith(">")
        and context.lines[index + 1].text.startswith(">")
    )


def _blank_around(
    rule_id: str,
    name: str,
    context: MarkdownLintContext,
    predicate: Callable[[str], bool],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return diagnostics for blocks not surrounded by blank lines."""
    return tuple(
        _block_diagnostic(rule_id, name, line.number)
        for index, line in enumerate(context.lines)
        if predicate(line.text)
        and not _has_surrounding_blanks(context.lines, index, predicate)
    )


def _has_surrounding_blanks(
    lines: tuple[MarkdownLine, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has acceptable surrounding lines."""
    return _has_blank_before(lines, index, predicate) and _has_blank_after(
        lines,
        index,
        predicate,
    )


def _block_diagnostic(
    rule_id: str,
    name: str,
    line: int,
) -> MarkdownDiagnostic:
    """Return one blank-around diagnostic."""
    return diagnostic(rule_id, name, line, "Surround block with blank lines.")


def _has_blank_before(
    lines: tuple[MarkdownLine, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has an acceptable preceding line."""
    if index == 0:
        return True
    text = lines[index - 1].text
    return is_blank(text) or predicate(text)


def _has_blank_after(
    lines: tuple[MarkdownLine, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has an acceptable following line."""
    if index + 1 >= len(lines):
        return True
    text = lines[index + 1].text
    return is_blank(text) or predicate(text)
