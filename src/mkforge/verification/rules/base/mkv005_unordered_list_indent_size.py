"""MKV005: Unordered list indentation.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.config import int_config
from mkforge.diagnostics.patterns import LIST_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV005"
NAME = "Unordered list indentation"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report unordered-list indentation not divisible by configured indent.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    indent = int_config(context.rule_config(RULE_ID).get("indent", 2), 2)
    return tuple(
        diagnostic(
            RULE_ID,
            NAME,
            line.number,
            f"Use {indent}-space indentation.",
            MARKDOWN_CATEGORY,
        )
        for line in context.lines
        if _bad_unordered_indent(line.text, indent)
    )


def _bad_unordered_indent(text: str, indent: int) -> bool:
    """Return whether an unordered list line violates indentation.

    Args:
        text: Source line text.
        indent: Expected indentation size.

    Returns:
        True when an unordered list line violates indentation.
    """
    match = LIST_RE.match(text)
    return bool(match and match.group(3) and len(match.group(1)) % indent)
