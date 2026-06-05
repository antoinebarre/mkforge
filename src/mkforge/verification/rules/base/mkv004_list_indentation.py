"""MKV004: List indentation.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.diagnostics.patterns import LIST_RE
from mkforge.diagnostics.reporting import diagnostic
from mkforge.verification.profiles import MARKDOWN_CATEGORY

RULE_ID = "MKV004"
NAME = "List indentation"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report inconsistent list indentation.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    indents: dict[int, int] = {}
    diagnostics: list[Diagnostic] = []
    for line in context.lines:
        match = LIST_RE.match(line.text)
        if match and _indent_is_inconsistent(indents, match.group(1)):
            diagnostics.append(
                diagnostic(
                    RULE_ID,
                    NAME,
                    line.number,
                    "Align list indentation at the same level.",
                    MARKDOWN_CATEGORY,
                ),
            )
    return tuple(diagnostics)


def _indent_is_inconsistent(indents: dict[int, int], indent_text: str) -> bool:
    """Return whether an indent conflicts with prior indentation.

    Args:
        indents: Function input.
        indent_text: Captured indentation text.

    Returns:
        True when an indent conflicts with prior indentation.
    """
    level = len(indent_text) // 2
    indent = len(indent_text)
    inconsistent = level in indents and indents[level] != indent
    indents.setdefault(level, indent)
    return inconsistent
