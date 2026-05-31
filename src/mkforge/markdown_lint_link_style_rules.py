"""Link style Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md054(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report disabled link/image styles."""
    config = context.rule_config("MD054")
    return tuple(
        diagnostic
        for line in context.lines
        for diagnostic in _line_style_diagnostics(
            line.number,
            line.text,
            config,
        )
    )


def _line_style_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return link style diagnostics for one line."""
    return (
        *_inline_diagnostics(line, text, config),
        *_full_reference_diagnostics(line, text, config),
    )


def _inline_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return inline-link style diagnostics for one line."""
    if _disabled(config, "inline") and _has_inline_link(text):
        return (_style_diagnostic(line, "Inline"),)
    return ()


def _full_reference_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[MarkdownDiagnostic, ...]:
    """Return full-reference style diagnostics for one line."""
    if _disabled(config, "full") and _has_full_reference(text):
        return (_style_diagnostic(line, "Full reference"),)
    return ()


def _disabled(config: Mapping[str, object], key: str) -> bool:
    """Return whether a link style option is disabled."""
    return config.get(key) is False


def _style_diagnostic(line: int, style: str) -> MarkdownDiagnostic:
    """Return a link style diagnostic."""
    return diagnostic(
        "MD054",
        "Link image style",
        line,
        f"{style} links/images are disabled.",
    )


def _has_inline_link(text: str) -> bool:
    """Return whether text contains an inline link or image."""
    return re.search(r"!?\[[^\]]+\]\([^)]+\)", text) is not None


def _has_full_reference(text: str) -> bool:
    """Return whether text contains a full reference link or image."""
    return re.search(r"!?\[[^\]]+\]\[[^\]]+\]", text) is not None
