"""MKC012: Link image style.

This rule is part of MkForge content validation. It checks document
policy rather than Markdown syntax: headings, links, naming,
accessibility text, or project-specific content constraints. The rule
emits a diagnostic when the document content does not satisfy that
policy.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from mkforge.diagnostics import Diagnostic, SourceContext
from mkforge.verification.profiles import VALIDATION_CATEGORY
from mkforge.verification.reporting import diagnostic

RULE_ID = "MKC012"
NAME = "Link image style"


def check(context: SourceContext) -> tuple[Diagnostic, ...]:
    """Report disabled link or image styles.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Diagnostics emitted by this rule.
    """
    config = context.rule_config(RULE_ID)
    return tuple(
        diagnostic
        for line in context.lines
        for diagnostic in _line_diagnostics(line.number, line.text, config)
    )


def _line_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[Diagnostic, ...]:
    """Return link style diagnostics for one line.

    Args:
        line: One-based source line number.
        text: Source line text.
        config: Optional per-rule configuration mapping.

    Returns:
        Link style diagnostics for one line.
    """
    return (
        *_inline_diagnostics(line, text, config),
        *_full_reference_diagnostics(line, text, config),
    )


def _inline_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[Diagnostic, ...]:
    """Return inline style diagnostics for one line.

    Args:
        line: One-based source line number.
        text: Source line text.
        config: Optional per-rule configuration mapping.

    Returns:
        Inline style diagnostics for one line.
    """
    if config.get("inline") is False and _has_inline_link(text):
        return (_style_diagnostic(line, "Inline"),)
    return ()


def _full_reference_diagnostics(
    line: int,
    text: str,
    config: Mapping[str, object],
) -> tuple[Diagnostic, ...]:
    """Return full-reference style diagnostics for one line.

    Args:
        line: One-based source line number.
        text: Source line text.
        config: Optional per-rule configuration mapping.

    Returns:
        Full-reference style diagnostics for one line.
    """
    if config.get("full") is False and _has_full_reference(text):
        return (_style_diagnostic(line, "Full reference"),)
    return ()


def _style_diagnostic(line: int, style: str) -> Diagnostic:
    """Return one style diagnostic.

    Args:
        line: One-based source line number.
        style: Link style label.

    Returns:
        One style diagnostic.
    """
    message = f"{style} links/images are disabled."
    return diagnostic(RULE_ID, NAME, line, message, VALIDATION_CATEGORY)


def _has_inline_link(text: str) -> bool:
    """Return whether text contains an inline link or image.

    Args:
        text: Source line text.

    Returns:
        True when text contains an inline link or image.
    """
    return re.search(r"!?\[[^\]]+\]\([^)]+\)", text) is not None


def _has_full_reference(text: str) -> bool:
    """Return whether text contains a full reference link or image.

    Args:
        text: Source line text.

    Returns:
        True when text contains a full reference link or image.
    """
    return re.search(r"!?\[[^\]]+\]\[[^\]]+\]", text) is not None
