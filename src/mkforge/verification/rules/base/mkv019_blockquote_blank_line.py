"""MKV019: Blank line in blockquote.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.diagnostics.text import is_blank
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV019"
NAME = "Blank line in blockquote"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report blank lines inside adjacent blockquotes.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    diagnostics: list[Diagnostic] = []
    for index, line in enumerate(context.lines[1:-1], start=1):
        if _is_blank_between_quotes(context, index, line.text):
            diagnostics.append(
                diagnostic(
                    RULE_ID,
                    NAME,
                    line.number,
                    "Use > on blank quote lines.",
                    MARKDOWN_CATEGORY,
                ),
            )
    return tuple(diagnostics)


def _is_blank_between_quotes(
    context: SourceContext,
    index: int,
    text: str,
) -> bool:
    """Return whether a blank line separates adjacent blockquote lines.

    Args:
        context: Parsed source context and rule configuration.
        index: Zero-based line index.
        text: Source line text.

    Returns:
        True when a blank line separates adjacent blockquote lines.
    """
    return (
        is_blank(text)
        and context.lines[index - 1].text.startswith(">")
        and context.lines[index + 1].text.startswith(">")
    )
