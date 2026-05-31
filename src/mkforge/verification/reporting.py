"""Helpers that create diagnostics from parsed Markdown lines."""

import re
from collections.abc import Callable

from mkforge.diagnostics import Diagnostic, Line, SourceContext


def diagnostic(
    rule_id: str,
    name: str,
    line: int,
    message: str,
    category: str,
) -> Diagnostic:
    """Create one source diagnostic.

    Args:
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        line: One-based source line number.
        message: Diagnostic message.
        category: Diagnostic category.

    Returns:
        Diagnostic instance.
    """
    return Diagnostic(rule_id, name, line, 1, message, category)


def pattern_diagnostics(
    context: SourceContext,
    *,
    rule_id: str,
    name: str,
    pattern: re.Pattern[str],
    category: str,
) -> tuple[Diagnostic, ...]:
    """Return diagnostics for non-code lines matching a pattern.

    Args:
        context: Parsed source context and rule configuration.
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        pattern: Compiled pattern used by the rule.
        category: Diagnostic category.

    Returns:
        Diagnostics for matching lines.
    """
    return tuple(
        diagnostic(rule_id, name, line.number, name, category)
        for line in context.lines
        if not line.in_code and pattern.search(line.text)
    )


def line_diagnostics(
    context: SourceContext,
    *,
    rule_id: str,
    name: str,
    category: str,
    predicate: Callable[[Line], bool],
) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines matching a predicate.

    Args:
        context: Parsed source context and rule configuration.
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        category: Diagnostic category.
        predicate: Predicate selecting source lines.

    Returns:
        Diagnostics for matching lines.
    """
    return tuple(
        diagnostic(rule_id, name, line.number, name, category)
        for line in context.lines
        if predicate(line)
    )
