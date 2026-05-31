"""List indentation Markdown lint rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic
from mkforge.markdown_lint_parser_patterns import LIST_RE

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md005(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report inconsistent list indentation."""
    indents: dict[int, int] = {}
    diagnostics: list[MarkdownDiagnostic] = []
    for line in context.lines:
        match = LIST_RE.match(line.text)
        if match and _indent_is_inconsistent(indents, match.group(1)):
            diagnostics.append(_indent_diagnostic(line.number))
    return tuple(diagnostics)


def rule_md007(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report unordered list indentation not divisible by configured indent."""
    indent = _indent_config(context.rule_config("MD007").get("indent", 2))
    return tuple(
        diagnostic(
            "MD007",
            "Unordered list indentation",
            line.number,
            f"Use {indent}-space indentation.",
        )
        for line in context.lines
        if _bad_unordered_indent(line.text, indent)
    )


def _bad_unordered_indent(text: str, indent: int) -> bool:
    """Return whether an unordered list line violates indentation."""
    match = LIST_RE.match(text)
    return bool(match and match.group(3) and len(match.group(1)) % indent)


def _indent_config(value: object) -> int:
    """Return a list indentation configuration value."""
    return int(value) if isinstance(value, str | int) else 2


def _indent_is_inconsistent(indents: dict[int, int], indent_text: str) -> bool:
    """Return whether an indent conflicts with prior list indentation."""
    level = len(indent_text) // 2
    indent = len(indent_text)
    inconsistent = level in indents and indents[level] != indent
    indents.setdefault(level, indent)
    return inconsistent


def _indent_diagnostic(line: int) -> MarkdownDiagnostic:
    """Return a list-indent diagnostic."""
    return diagnostic(
        "MD005",
        "List indentation",
        line,
        "Align list indentation at the same level.",
    )
