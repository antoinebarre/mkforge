"""Helpers that classify Markdown source text."""

import re

from mkforge.diagnostics.patterns import HR_RE, LIST_RE


def is_blank(text: str) -> bool:
    """Return whether a line is blank.

    Args:
        text: Source line text.

    Returns:
        True when the line contains only whitespace.
    """
    return not text.strip()


def is_fence(text: str) -> bool:
    """Return whether a line starts a fenced code block.

    Args:
        text: Source line text.

    Returns:
        True when the line starts with a backtick or tilde fence marker.
    """
    return re.match(r"^\s*(`{3,}|~{3,})", text) is not None


def is_horizontal_rule(text: str) -> bool:
    """Return whether a line appears to be a horizontal rule.

    Args:
        text: Source line text.

    Returns:
        True when the line matches a Markdown horizontal rule.
    """
    return HR_RE.match(text) is not None


def is_list_item(text: str) -> bool:
    """Return whether a line is a Markdown list item.

    Args:
        text: Source line text.

    Returns:
        True when the line starts with an ordered or unordered list marker.
    """
    return LIST_RE.match(text) is not None


def visible_text(text: str) -> str:
    """Return text with simple inline syntax removed.

    Args:
        text: Source line text.

    Returns:
        Text after removing simple code spans, images, and inline links.
    """
    value = re.sub(r"`[^`]*`", "", text)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    return re.sub(r"\[[^\]]+\]\([^)]+\)", "", value)
