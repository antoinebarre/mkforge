"""Markdown frontmatter rendering helpers."""

from mkforge.containers import Metadata


def render_metadata(metadata: Metadata) -> str:
    """Render metadata as YAML frontmatter.

    Args:
        metadata: Metadata to render.

    Returns:
        YAML frontmatter block.
    """
    lines = ["---"]
    _append_scalar(lines, "title", metadata.title)
    _append_scalar(lines, "author", metadata.author)
    _append_scalar(lines, "date", metadata.date)
    _append_scalar(lines, "version", metadata.version)
    _append_scalar(lines, "description", metadata.description)
    _append_tags(lines, metadata.tags)
    lines.append("---")
    return "\n".join(lines)


def _append_scalar(lines: list[str], key: str, value: str | None) -> None:
    """Append a scalar metadata field if present.

    Args:
        lines: Mutable line accumulator.
        key: Metadata key.
        value: Optional metadata value.
    """
    if value is not None:
        lines.append(f"{key}: {value}")


def _append_tags(lines: list[str], tags: tuple[str, ...]) -> None:
    """Append metadata tags if present.

    Args:
        lines: Mutable line accumulator.
        tags: Optional tag values.
    """
    if not tags:
        return
    lines.append("tags:")
    lines.extend(f"  - {tag}" for tag in tags)
