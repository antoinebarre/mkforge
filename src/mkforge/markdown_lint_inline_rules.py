"""Inline Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, visible_text

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md033(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inline HTML."""
    pattern = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(\s|>|/>)")
    return _pattern_rule(context, "MD033", "Inline HTML", pattern)


def rule_md034(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report bare URLs."""
    pattern = re.compile(r"(?<![<(])(https?://[^\s>)]+|[\w.+-]+@[\w.-]+\.\w+)")
    return _pattern_rule(
        context,
        "MD034",
        "Bare URL used",
        pattern,
        use_visible_text=True,
    )


def rule_md037(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report spaces inside emphasis markers."""
    pattern = re.compile(r"(\*\s+[^*]+\s+\*)|(_\s+[^_]+\s+_)")
    return _pattern_rule(context, "MD037", "Spaces inside emphasis", pattern)


def rule_md038(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report spaces inside code spans."""
    pattern = re.compile(r"`\s+\S[^`]*`|`\S[^`]*\s+`")
    return _pattern_rule(context, "MD038", "Spaces inside code span", pattern)


def rule_md039(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report spaces inside link text."""
    pattern = re.compile(r"\[\s+[^\]]+\s+\]\([^)]+\)")
    return _pattern_rule(context, "MD039", "Spaces inside link text", pattern)


def rule_md042(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report empty links."""
    pattern = re.compile(r"\[[^\]]+\]\((#?)\)")
    return _pattern_rule(context, "MD042", "No empty links", pattern)


def rule_md045(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report images without alternate text."""
    pattern = re.compile(r"!\[\]\([^)]+\)|<img(?![^>]*\balt=)[^>]*>")
    return _pattern_rule(
        context,
        "MD045",
        "Images should have alternate text",
        pattern,
    )


def rule_md059(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report generic link text."""
    prohibited = {
        str(item).lower()
        for item in _string_items(
            context.rule_config("MD059").get(
                "prohibited_texts",
                ["click here", "here", "link", "more"],
            ),
        )
    }
    matches = re.finditer(r"\[([^\]]+)\]\([^)]+\)", context.source)
    return tuple(
        diagnostic(
            "MD059",
            "Descriptive link text",
            _line_for_offset(context.source, match.start()),
            "Use descriptive link text.",
        )
        for match in matches
        if match.group(1).strip().lower() in prohibited
    )


def _pattern_rule(
    context: MarkdownLintContext,
    rule_id: str,
    name: str,
    pattern: re.Pattern[str],
    *,
    use_visible_text: bool = False,
) -> tuple[MarkdownDiagnostic, ...]:
    """Apply one regex pattern to non-code lines."""
    return tuple(
        diagnostic(rule_id, name, line.number, name)
        for line in context.lines
        if not line.in_code
        and pattern.search(
            _lint_text(line.text, use_visible_text=use_visible_text),
        )
    )


def _lint_text(text: str, *, use_visible_text: bool) -> str:
    """Return the rule-specific text surface for a line."""
    return visible_text(text) if use_visible_text else text


def _string_items(value: object) -> list[str]:
    """Return string values from a sequence-like configuration value."""
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value]
    return []


def _line_for_offset(source: str, offset: int) -> int:
    """Return one-based line number for a source offset."""
    return source.count("\n", 0, offset) + 1
