"""Shared Markdown block spacing diagnostics."""

from __future__ import annotations

from collections.abc import Callable

from mkforge.diagnostics import Diagnostic, Line, SourceContext
from mkforge.verification.reporting import diagnostic
from mkforge.verification.text import is_blank

_BLANK_MESSAGE = "Surround block with blank lines."


def block_spacing_diagnostics(
    context: SourceContext,
    *,
    rule_id: str,
    name: str,
    category: str,
    predicate: Callable[[str], bool],
) -> tuple[Diagnostic, ...]:
    """Return diagnostics for blocks not surrounded by blank lines.

    Args:
        context: Parsed source context and rule configuration.
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        category: Diagnostic category.
        predicate: Predicate selecting source lines.

    Returns:
        Diagnostics for blocks with missing spacing.
    """
    return tuple(
        diagnostic(rule_id, name, line.number, _BLANK_MESSAGE, category)
        for index, line in enumerate(context.lines)
        if predicate(line.text)
        and not _has_surrounding_blanks(context.lines, index, predicate)
    )


def _has_surrounding_blanks(
    lines: tuple[Line, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has acceptable surrounding lines.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.
        predicate: Predicate selecting source lines.

    Returns:
        True when a block has acceptable surrounding lines.
    """
    return _valid_previous(lines, index, predicate) and _valid_next(
        lines,
        index,
        predicate,
    )


def _valid_previous(
    lines: tuple[Line, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has an acceptable previous line.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.
        predicate: Predicate selecting source lines.

    Returns:
        True when a block has an acceptable previous line.
    """
    if index == 0:
        return True
    text = lines[index - 1].text
    return is_blank(text) or predicate(text)


def _valid_next(
    lines: tuple[Line, ...],
    index: int,
    predicate: Callable[[str], bool],
) -> bool:
    """Return whether a block has an acceptable next line.

    Args:
        lines: Parsed source lines.
        index: Zero-based line index.
        predicate: Predicate selecting source lines.

    Returns:
        True when a block has an acceptable next line.
    """
    if index + 1 >= len(lines):
        return True
    text = lines[index + 1].text
    return is_blank(text) or predicate(text)
