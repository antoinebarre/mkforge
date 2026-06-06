"""Explicit exceptions raised by MkForge report validation."""

from __future__ import annotations

from pathlib import Path


class MkForgeError(Exception):
    """Base exception for MkForge errors."""


class InvalidChildError(MkForgeError):
    """Raised when a container receives an unsupported child node.

    Args:
        parent: Name of the parent container type.
        child: Name of the unsupported child type.
    """

    def __init__(self, parent: str, child: str) -> None:
        """Initialize an invalid child error."""
        self.parent = parent
        self.child = child
        super().__init__(parent, child)

    def __str__(self) -> str:
        """Return a precise invalid child message."""
        return f"{self.parent} cannot contain {self.child}."


class InvalidTableError(MkForgeError):
    """Raised when table data cannot be rendered as valid GFM."""


class ReportDepthError(MkForgeError):
    """Raised when a section nesting level would exceed Markdown H6.

    Args:
        level: The computed heading level.
    """

    def __init__(self, level: int) -> None:
        """Initialize a report depth error."""
        super().__init__(
            f"Section nesting renders as H{level}; maximum is H6.",
        )


class DownloadAssetError(MkForgeError):
    """Raised when a remote image URL cannot be downloaded at save time.

    Attributes:
        url: The URL that could not be fetched.
        reason: Human-readable failure description.
    """

    def __init__(self, url: str, reason: str) -> None:
        """Initialize a download asset error.

        Args:
            url: The URL that failed to download.
            reason: Description of the failure.
        """
        self.url = url
        self.reason = reason
        super().__init__(url, reason)

    def __str__(self) -> str:
        """Return a precise download failure message."""
        return f"Failed to download asset {self.url!r}: {self.reason}"


class MissingAssetError(MkForgeError):
    """Raised when one or more local image paths cannot be found at save time.

    Attributes:
        missing: Tuple of resolved paths that do not exist on disk.
    """

    def __init__(self, missing: list[Path]) -> None:
        """Initialize a missing asset error.

        Args:
            missing: List of resolved paths that were not found.
        """
        self.missing: tuple[Path, ...] = tuple(missing)
        paths_text = ", ".join(str(p) for p in self.missing)
        super().__init__(f"Missing asset files: {paths_text}")
