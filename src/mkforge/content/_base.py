"""Base protocol and shared constants for Markdown content elements.

Defines the ``Renderable`` protocol that every content element must satisfy.
Any class with a ``render() -> str`` method implicitly satisfies this protocol.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Renderable(Protocol):
    """Protocol for objects that can render themselves to Markdown.

    Every content element in the ``mkforge.content`` package satisfies this
    protocol by implementing ``render() -> str``.
    """

    def render(self) -> str:
        """Render the element to a Markdown string.

        Returns:
            Markdown representation of the element.
        """
        ...  # pragma: no cover  — Protocol stub; never executed at runtime
