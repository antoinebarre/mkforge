"""MKV032: Emphasis style.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

import re

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKV032"
NAME = "Emphasis style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report mixed emphasis styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return _mixed_inline_style(
        context,
        r"(?<!\*)\*[^*]+\*(?!\*)",
        r"(?<!_)_[^_]+_(?!_)",
    )


def _mixed_inline_style(
    context: SourceContext,
    first_pattern: str,
    second_pattern: str,
) -> tuple[Diagnostic, ...]:
    """Return a diagnostic when both inline styles are present.

    Args:
        context: Parsed source context and rule configuration.
        first_pattern: Function input.
        second_pattern: Function input.

    Returns:
        A diagnostic when both inline styles are present.
    """
    source = "\n".join(line.text for line in context.lines if not line.in_code)
    if re.search(first_pattern, source) and re.search(second_pattern, source):
        return (
            diagnostic(
                RULE_ID,
                NAME,
                1,
                "Use one emphasis style.",
                MARKDOWN_CATEGORY,
            ),
        )
    return ()
