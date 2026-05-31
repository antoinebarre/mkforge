"""MKV009: Multiple blank lines.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic
from mkforge.verification.text import is_blank

RULE_ID = "MKV009"
NAME = "Multiple blank lines"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report multiple consecutive blank lines.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    diagnostics: list[Diagnostic] = []
    blank_count = 0
    for line in context.lines:
        blank_count = _next_blank_count(
            blank_count,
            line.text,
            in_code=line.in_code,
        )
        if blank_count > 1:
            diagnostics.append(
                diagnostic(
                    RULE_ID,
                    NAME,
                    line.number,
                    "Remove extra blank line.",
                    MARKDOWN_CATEGORY,
                ),
            )
    return tuple(diagnostics)


def _next_blank_count(count: int, text: str, *, in_code: bool) -> int:
    """Return the updated consecutive blank line count.

    Args:
        count: Current count value.
        text: Source line text.
        in_code: Whether the line is inside a fenced code block.

    Returns:
        The updated consecutive blank line count.
    """
    if is_blank(text) and not in_code:
        return count + 1
    return 0
