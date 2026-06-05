"""MKV016: Blanks around headings.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, Heading, Line, SourceContext
from mkforge.diagnostics.reporting import diagnostic
from mkforge.diagnostics.text import is_blank
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV016"
NAME = "Blanks around headings"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report headings not surrounded by blank lines.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            heading.line,
            "Surround headings with blank lines.",
            MARKDOWN_CATEGORY,
        )
        for heading in context.headings
        if not _has_blank_lines(context.lines, heading)
    )


def _has_blank_lines(lines: tuple[Line, ...], heading: Heading) -> bool:
    """Return whether a heading has acceptable surrounding lines.

    Args:
        lines: Parsed source lines.
        heading: Parsed heading to inspect.

    Returns:
        True when a heading has acceptable surrounding lines.
    """
    index = heading.line - 1
    before = index == 0 or is_blank(lines[index - 1].text)
    after = index + 1 >= len(lines) or is_blank(lines[index + 1].text)
    return before and after
