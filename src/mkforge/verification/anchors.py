"""Helpers that resolve Markdown heading anchors."""

from mkforge.diagnostics import SourceContext
from mkforge.table_of_contents import anchor_slug


def heading_slugs(context: SourceContext) -> set[str]:
    """Return GitHub-like heading slugs for a context.

    Args:
        context: Parsed source context and rule configuration.

    Returns:
        Known heading anchor slugs.
    """
    seen: dict[str, int] = {}
    slugs: set[str] = {"top"}
    for heading in context.headings:
        base = anchor_slug(heading.text)
        count = seen.get(base, 0)
        seen[base] = count + 1
        slugs.add(base if count == 0 else f"{base}-{count}")
    return slugs


def line_for_offset(source: str, offset: int) -> int:
    """Return the one-based line number for a source offset.

    Args:
        source: Markdown source text.
        offset: Zero-based source character offset.

    Returns:
        One-based line number.
    """
    return source.count("\n", 0, offset) + 1
