"""Parser for ATX Markdown headings."""

from mkforge.diagnostics.models import Heading, Line
from mkforge.diagnostics.patterns import ATX_HEADING_RE


def parse_atx_heading(line: Line) -> Heading | None:
    """Parse one ATX heading.

    Args:
        line: Parsed source line.

    Returns:
        Parsed heading, or None when the line is not an ATX heading.
    """
    match = ATX_HEADING_RE.match(line.text)
    if match is None:
        return None
    return Heading(
        line.number,
        len(match.group(1)),
        match.group(3).strip(),
        "atx",
    )
