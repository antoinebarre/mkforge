"""MD024 and MD025 check heading uniqueness and top-level count.

These two rules belong together because they both constrain the set of
headings at a given level:
- MD024: heading text must be unique across the document.
- MD025: only one heading at the configured top level is allowed.
Each rule emits one diagnostic per violating heading.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _headings,
    _int_option,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD024 and MD025 heading uniqueness diagnostics.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for duplicate or multiple top-level headings.
    """
    return (
        *_duplicate_headings(source),
        *_multiple_top_level_headings(source),
    )


def _duplicate_headings(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return MD024 diagnostics for headings with duplicate text.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each heading whose text matches a prior heading.
    """
    seen: set[str] = set()
    diagnostics: list[Diagnostic] = []
    for heading in _headings(source):
        key = heading.text.casefold()
        if key in seen:
            diagnostics.append(
                _diagnostic(
                    "MD024",
                    heading.line,
                    1,
                    "Use unique heading text.",
                ),
            )
        seen.add(key)
    return tuple(diagnostics)


def _multiple_top_level_headings(
    source: MarkdownSource,
) -> tuple[Diagnostic, ...]:
    """Return MD025 diagnostics for multiple top-level headings.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each top-level heading beyond the first.
    """
    level = _int_option(source, "MD025", "level", 1)
    top_headings = [
        heading for heading in _headings(source) if heading.level == level
    ]
    return tuple(
        _diagnostic(
            "MD025",
            heading.line,
            1,
            f"Use only one level {level} heading.",
        )
        for heading in top_headings[1:]
    )
