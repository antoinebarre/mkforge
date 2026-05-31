"""Parser for setext Markdown headings."""

from mkforge.diagnostics import Heading, Line

SETEXT_H2_MIN_LENGTH = 3


def parse_setext_heading(
    lines: tuple[Line, ...],
    index: int,
) -> Heading | None:
    """Parse one setext heading marker.

    Args:
        lines: Parsed source lines.
        index: Zero-based marker line index.

    Returns:
        Parsed heading, or None when the marker is not a setext heading.
    """
    if not _can_parse_setext(lines, index):
        return None
    previous = lines[index - 1]
    level = _setext_level(lines[index].text.strip())
    if level is None:
        return None
    return Heading(previous.number, level, previous.text.strip(), "setext")


def _setext_level(marker: str) -> int | None:
    """Return heading level for a setext marker.

    Args:
        marker: Setext heading marker text.

    Returns:
        Heading level, or None when the marker is invalid.
    """
    if set(marker) == {"="}:
        return 1
    if set(marker) == {"-"} and len(marker) >= SETEXT_H2_MIN_LENGTH:
        return 2
    return None


def _can_parse_setext(lines: tuple[Line, ...], index: int) -> bool:
    """Return whether a line can be a setext marker.

    Args:
        lines: Parsed source lines.
        index: Zero-based marker line index.

    Returns:
        True when the current line can annotate the previous line as setext.
    """
    if index == 0 or lines[index].in_code:
        return False
    previous = lines[index - 1]
    return bool(previous.text.strip()) and not previous.in_code
