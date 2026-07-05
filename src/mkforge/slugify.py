"""Heading-to-anchor slugification.

Provides ``slugify_heading``, the public conversion from a raw Markdown
heading title to a GitHub-compatible HTML anchor slug. Downstream tools such
as scribpy use this to link into assembled Markdown documents by heading
text.
"""

from __future__ import annotations

import re

from mkforge.input_checks import require_string

_INLINE_MARKDOWN_MARKERS = re.compile(r"[`*_~]")
_NON_ALPHANUMERIC_RUN = re.compile(r"[^\w-]+", flags=re.UNICODE)
_LEADING_OR_TRAILING_HYPHENS = re.compile(r"^-+|-+$")


def slugify_heading(text: str) -> str:
    """Convert a raw Markdown heading title to a GitHub-style anchor slug.

    Follows the GitHub Markdown anchor algorithm: the text is lowercased,
    inline Markdown markers (backticks, asterisks, underscores, tildes) are
    stripped, every run of characters that is neither alphanumeric nor a
    hyphen is collapsed to a single hyphen, and leading or trailing hyphens
    are removed. Unicode letters (accents, ideograms) are preserved and only
    case-folded, never transliterated.

    Args:
        text: Raw heading text, without the leading ``#`` markers.

    Returns:
        Lowercase, hyphen-separated anchor slug suitable for use as an HTML
        anchor (e.g. in a ``#slug`` link).

    Raises:
        TypeError: If ``text`` is not a string.
    """
    require_string(text, "text", allow_empty=True)
    stripped = _INLINE_MARKDOWN_MARKERS.sub("", text)
    lowered = stripped.lower()
    hyphenated = _NON_ALPHANUMERIC_RUN.sub("-", lowered)
    return _LEADING_OR_TRAILING_HYPHENS.sub("", hyphenated)
