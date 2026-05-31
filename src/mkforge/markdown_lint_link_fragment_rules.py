"""Link-fragment Markdown lint rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mkforge.markdown_lint_helpers import diagnostic, heading_slugs

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownLintContext,
    )


def rule_md051(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
    """Report invalid local link fragments."""
    slugs = heading_slugs(context)
    return tuple(
        diagnostic(
            "MD051",
            "Link fragments",
            line.number,
            "Link fragment does not match a heading.",
        )
        for line in context.lines
        for fragment in re.findall(r"\[[^\]]+\]\(#([^)]+)\)", line.text)
        if fragment not in slugs and not re.match(r"L\d+", fragment)
    )
