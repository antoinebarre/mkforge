"""MD035 checks that horizontal rules use a consistent style.

This rule belongs to Markdown verification because mixing horizontal rule
styles (``---``, ``***``, ``___``) reduces document consistency. It emits
one diagnostic for each horizontal rule whose style differs from the
configured or detected expectation.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    HORIZONTAL_RULE,
    _diagnostic,
)
from mkforge.verification.source_scan import lines_outside_fenced_code


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for horizontal rules with inconsistent style.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for horizontal rules that differ from the expected style.
    """
    style = str(source.rule_options("MD035").get("style", "consistent"))
    expected = ""
    diagnostics: list[Diagnostic] = []
    for line in lines_outside_fenced_code(source):
        if not HORIZONTAL_RULE.match(line.text):
            continue
        expected = (
            line.text.strip()
            if style == "consistent" and not expected
            else expected
        )
        target = expected if style == "consistent" else style
        if line.text.strip() != target:
            diagnostics.append(
                _diagnostic(
                    "MD035",
                    line.number,
                    1,
                    f"Use {target} horizontal rules.",
                ),
            )
    return tuple(diagnostics)
