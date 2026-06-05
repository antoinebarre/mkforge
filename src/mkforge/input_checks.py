"""Reusable input checks for public MkForge objects."""

from __future__ import annotations

from os import PathLike


def require_string(value: object, label: str, *, allow_empty: bool) -> None:
    """Validate a string value.

    Args:
        value: Candidate value.
        label: Human-readable value label.
        allow_empty: Whether blank strings are accepted.

    Raises:
        TypeError: If the value is not a string.
        ValueError: If the value is blank and blank values are rejected.
    """
    if not isinstance(value, str):
        message = f"{label} must be a string; got {type(value).__name__}."
        raise TypeError(message)
    if not allow_empty and not value.strip():
        message = f"{label} cannot be empty."
        raise ValueError(message)


def require_bool(value: object, label: str) -> None:
    """Validate a boolean value.

    Args:
        value: Candidate value.
        label: Human-readable value label.

    Raises:
        TypeError: If the value is not a boolean.
    """
    if not isinstance(value, bool):
        message = f"{label} must be a bool; got {type(value).__name__}."
        raise TypeError(message)


def require_tuple(value: object, label: str) -> None:
    """Validate a tuple value.

    Args:
        value: Candidate value.
        label: Human-readable value label.

    Raises:
        TypeError: If the value is not a tuple.
    """
    if not isinstance(value, tuple):
        message = f"{label} must be a tuple; got {type(value).__name__}."
        raise TypeError(message)


def require_path(value: object, label: str) -> None:
    """Validate a filesystem path input.

    Args:
        value: Candidate value.
        label: Human-readable value label.

    Raises:
        TypeError: If the value is not path-like.
        ValueError: If a string path is blank.
    """
    if not isinstance(value, str | PathLike):
        message = f"{label} must be str or PathLike."
        raise TypeError(message)
    if isinstance(value, str) and not value.strip():
        message = f"{label} cannot be empty."
        raise ValueError(message)


def require_metadata(value: object) -> None:
    """Validate optional report metadata.

    Args:
        value: Candidate value.

    Raises:
        TypeError: If metadata is not a dictionary or uses non-string keys.
        ValueError: If a metadata key is blank.
    """
    if value is None:
        return
    if not isinstance(value, dict):
        message = f"metadata must be a dict; got {type(value).__name__}."
        raise TypeError(message)
    for key in value:
        require_string(key, "metadata keys", allow_empty=False)
