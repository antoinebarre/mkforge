"""Explicit exceptions raised by MkForge report validation."""


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
