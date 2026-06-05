"""MKV029: Code block style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import FENCE_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV029"
NAME = "Code block style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed fenced and indented code block styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    if _has_fenced_code(context) and _has_indented_code(context):
        return (
            diagnostic(
                RULE_ID,
                NAME,
                1,
                "Use one code block style.",
                MARKDOWN_CATEGORY,
            ),
        )
    return ()


def _has_fenced_code(context: SourceContext) -> bool:
    """Return whether the source contains fenced code.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        True when the source contains fenced code.
    """
    return any(FENCE_RE.match(line.text) for line in context.lines)


def _has_indented_code(context: SourceContext) -> bool:
    """Return whether the source contains indented code.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        True when the source contains indented code.
    """
    return any(_is_indented_code(line.text) for line in context.lines)


def _is_indented_code(text: str) -> bool:
    """Return whether a line is an indented code block candidate.

    Args:
        text: Source line text.

    Returns:
        True when a line is an indented code block candidate.
    """
    return text.startswith("    ") and bool(text.strip())
