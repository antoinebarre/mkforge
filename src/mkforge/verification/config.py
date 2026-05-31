"""Helpers that read simple rule configuration values."""


def string_items(value: object) -> list[str]:
    """Return string values from a sequence-like configuration value.

    Args:
        value: Candidate value.

    Returns:
        String items extracted from the value.
    """
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value]
    return []


def int_config(value: object, default: int) -> int:
    """Return an integer configuration value.

    Args:
        value: Candidate value.
        default: Fallback integer value.

    Returns:
        Integer configuration value.
    """
    return int(value) if isinstance(value, str | int) else default
