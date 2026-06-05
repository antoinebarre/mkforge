"""Markdown frontmatter rendering helpers."""

from mkforge.input_checks import require_metadata, require_string


def render_metadata(metadata: dict[str, object]) -> str:
    """Render metadata as YAML frontmatter.

    Args:
        metadata: Dictionary to render.

    Returns:
        YAML frontmatter block.
    """
    require_metadata(metadata)
    lines = ["---"]
    for key, value in metadata.items():
        _append_value(lines, key, value)
    lines.append("---")
    return "\n".join(lines)


def _append_value(lines: list[str], key: str, value: object) -> None:
    """Append one metadata value.

    Args:
        lines: Mutable line accumulator.
        key: Metadata key.
        value: Metadata value.
    """
    require_string(key, "metadata key", allow_empty=False)
    if isinstance(value, list | tuple):
        _append_sequence(lines, key, value)
        return
    lines.append(f"{key}: {_scalar_text(value)}")


def _append_sequence(
    lines: list[str],
    key: str,
    value: list[object] | tuple[object, ...],
) -> None:
    """Append one sequence metadata value.

    Args:
        lines: Mutable line accumulator.
        key: Metadata key.
        value: Sequence metadata value.
    """
    lines.append(f"{key}:")
    lines.extend(f"  - {_scalar_text(item)}" for item in value)


def _scalar_text(value: object) -> str:
    """Render a scalar metadata value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
