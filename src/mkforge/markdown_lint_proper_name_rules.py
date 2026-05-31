"""Proper-name Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md044(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report configured proper-name capitalization mistakes."""
    names = _string_items(context.rule_config("MD044").get("names", []))
    return tuple(_proper_name_diagnostics(context, names))


def _string_items(value: object) -> list[str]:
    """Return string values from a sequence-like configuration value."""
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value]
    return []


def _proper_name_diagnostics(
    context: MarkdownLintContext,
    names: list[str],
) -> Iterator[MarkdownDiagnostic]:
    """Yield proper-name diagnostics for a context."""
    for line in context.lines:
        for name in names:
            yield from _proper_name_diagnostic(line.number, line.text, name)


def _proper_name_diagnostic(
    line: int,
    text: str,
    name: str,
) -> tuple[MarkdownDiagnostic, ...]:
    """Return a proper-name diagnostic when capitalization differs."""
    pattern = re.compile(re.escape(name), re.IGNORECASE)
    if pattern.search(text) and name not in text:
        return (
            diagnostic(
                "MD044",
                "Proper names",
                line,
                f"Use capitalization: {name}.",
            ),
        )
    return ()
