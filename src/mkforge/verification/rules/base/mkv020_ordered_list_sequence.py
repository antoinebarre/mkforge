"""MKV020: Ordered list prefix.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import LIST_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV020"
NAME = "Ordered list prefix"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report non-increasing ordered-list prefixes.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    expected = 1
    diagnostics: list[Diagnostic] = []
    for line in context.lines:
        expected, line_diagnostics = _check_ordered_line(
            expected,
            line.text,
            line.number,
        )
        diagnostics.extend(line_diagnostics)
    return tuple(diagnostics)


def _check_ordered_line(
    expected: int,
    text: str,
    line: int,
) -> tuple[int, tuple[Diagnostic, ...]]:
    """Return next expected number and diagnostics for one line.

    Args:
        expected: Expected table column count.
        text: Source line text.
        line: One-based source line number.

    Returns:
        Next expected number and diagnostics for one line.
    """
    match = LIST_RE.match(text)
    if not match or not match.group(4):
        return 1, ()
    actual = int(match.group(4))
    if actual != expected:
        return actual + 1, (
            diagnostic(
                RULE_ID,
                NAME,
                line,
                "Use increasing ordered-list numbers.",
                MARKDOWN_CATEGORY,
            ),
        )
    return actual + 1, ()
