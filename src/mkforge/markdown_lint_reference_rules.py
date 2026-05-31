"""Reference and naming Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md052(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report undefined reference labels."""
    definitions = _reference_definitions(context)
    used = _reference_uses(context)
    return tuple(
        diagnostic(
            "MD052",
            "Reference links/images",
            line,
            f"Reference label '{label}' is not defined.",
        )
        for label, line in used.items()
        if label not in definitions and label.lower() != "x"
    )


def rule_md053(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report unused reference definitions."""
    definitions = _reference_definitions(context)
    used = set(_reference_uses(context))
    return tuple(
        diagnostic(
            "MD053",
            "Reference definitions",
            line,
            f"Reference label '{label}' is not used.",
        )
        for label, line in definitions.items()
        if label not in used and label != "//"
    )


def _reference_definitions(context: MarkdownLintContext) -> dict[str, int]:
    """Return reference definition labels."""
    definitions: dict[str, int] = {}
    for line in context.lines:
        match = re.match(r"^\[([^\]]+)\]:", line.text)
        if match:
            definitions.setdefault(match.group(1).lower(), line.number)
    return definitions


def _reference_uses(context: MarkdownLintContext) -> dict[str, int]:
    """Return referenced labels."""
    uses: dict[str, int] = {}
    for line in context.lines:
        for label in re.findall(r"!?\[[^\]]+\]\[([^\]]*)\]", line.text):
            if label:
                uses.setdefault(label.lower(), line.number)
    return uses
