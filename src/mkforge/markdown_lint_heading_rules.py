"""Heading syntax Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic
from mkforge.markdown_lint_parser_patterns import BAD_ATX_RE

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md018(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report missing space after ATX heading marker."""
    return tuple(
        diagnostic(
            "MD018",
            "No space after hash",
            line.number,
            "Add a space after heading marker.",
        )
        for line in context.lines
        if BAD_ATX_RE.match(line.text)
    )


def rule_md019(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report multiple spaces after ATX heading marker."""
    pattern = re.compile(r"^#{1,6} {2,}\S")
    return _pattern_rule(
        context,
        "MD019",
        "Multiple spaces after hash",
        pattern,
    )


def rule_md020(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report missing spaces in closed ATX headings."""
    pattern = re.compile(r"^#{1,6}\S.*#+$|^#{1,6} .*[^ ]#+$")
    return _pattern_rule(
        context,
        "MD020",
        "Missing space in closed ATX",
        pattern,
    )


def rule_md021(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report multiple spaces in closed ATX headings."""
    pattern = re.compile(r"^#{1,6} {2,}.*#+$|^#{1,6} .* {2,}#+\s*$")
    return _pattern_rule(
        context,
        "MD021",
        "Multiple spaces in closed ATX",
        pattern,
    )


def rule_md023(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report indented headings."""
    pattern = re.compile(r"^\s+#{1,6}\s")
    return _pattern_rule(context, "MD023", "Heading start left", pattern)


def rule_md026(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report trailing punctuation in headings."""
    punctuation = str(context.rule_config("MD026").get("punctuation", ".,;:!"))
    return tuple(
        diagnostic(
            "MD026",
            "Trailing punctuation in heading",
            heading.line,
            "Remove trailing punctuation.",
        )
        for heading in context.headings
        if heading.text.endswith(tuple(punctuation))
    )


def rule_md027(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report multiple spaces after blockquote marker."""
    pattern = re.compile(r"^>\s{2,}\S")
    return _pattern_rule(
        context,
        "MD027",
        "Multiple spaces after blockquote",
        pattern,
    )


def _pattern_rule(
    context: MarkdownLintContext,
    rule_id: str,
    name: str,
    pattern: re.Pattern[str],
) -> tuple[MarkdownDiagnostic, ...]:
    """Apply one regex pattern to non-code lines."""
    return tuple(
        diagnostic(rule_id, name, line.number, name)
        for line in context.lines
        if not line.in_code and pattern.search(line.text)
    )
