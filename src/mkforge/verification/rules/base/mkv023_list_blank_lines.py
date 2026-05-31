"""MKV023: Blanks around lists.

This rule is part of MkForge source verification. It checks the Markdown
source shape before any document-specific policy is applied. The check
emits a diagnostic when the source uses a syntax form that is
inconsistent, ambiguous, or outside the selected Markdown/GFM profile.
"""

from __future__ import annotations

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.block_spacing import (
    block_spacing_diagnostics,
)
from mkforge.verification.profiles import MARKDOWN_CATEGORY
from mkforge.verification.text import is_list_item

RULE_ID = "MKV023"
NAME = "Blanks around lists"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report lists not surrounded by blank lines.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    return block_spacing_diagnostics(
        context,
        rule_id=RULE_ID,
        name=NAME,
        category=MARKDOWN_CATEGORY,
        predicate=is_list_item,
    )
