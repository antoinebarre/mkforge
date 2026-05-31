"""MKV011: Command prompts.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.reporting import line_diagnostics

RULE_ID = "MKV011"
NAME = "Command prompts"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report shell prompts in command-only code blocks.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return line_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        category=MARKDOWN_CATEGORY,
        predicate=lambda line: line.in_code and line.text.startswith("$ "),
    )
