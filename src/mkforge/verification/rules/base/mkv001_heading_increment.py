"""MKV001: Heading increment.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV001"
NAME = "Heading increment"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Check that heading levels do not skip intermediate levels.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    diagnostics: list[Diagnostic] = []
    previous = 0
    for heading in context.headings:
        if previous and heading.level > previous + 1:
            diagnostics.append(
                diagnostic(
                    RULE_ID,
                    NAME,
                    heading.line,
                    "Do not skip heading levels.",
                    MARKDOWN_CATEGORY,
                ),
            )
        previous = heading.level
    return tuple(diagnostics)
