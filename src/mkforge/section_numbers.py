"""Automatic heading numbering for Markdown reports."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NumberingContext:
    """Track heading counters while traversing a report tree.

    Attributes:
        counters: Current stack of sibling counters.
    """

    counters: list[int] = field(default_factory=list)

    def enter_level(self) -> None:
        """Enter a deeper heading level."""
        self.counters.append(0)

    def leave_level(self) -> None:
        """Leave the current heading level."""
        self.counters.pop()

    def advance(self) -> None:
        """Advance the current sibling counter."""
        self.counters[-1] += 1

    def prefix(self) -> str:
        """Return the dotted prefix for the current heading.

        Returns:
            A dotted prefix such as ``1.2.``.
        """
        return ".".join(str(counter) for counter in self.counters) + "."


def numbered_title(title: str, context: NumberingContext) -> str:
    """Prefix a heading title with the active numbering context.

    Args:
        title: Raw heading title.
        context: Active numbering context.

    Returns:
        Numbered heading title.
    """
    return f"{context.prefix()} {title}"
