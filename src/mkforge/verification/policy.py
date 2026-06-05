"""Markdown conformance policies and source context."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from mkforge.verification.settings import (
    VerificationSettings,
    default_settings,
)


@dataclass(frozen=True)
class Diagnostic:
    """One Markdown conformance diagnostic.

    Attributes:
        rule_id: Stable conformance rule identifier.
        name: Human-readable rule name.
        line: One-based source line number.
        column: One-based source column number.
        message: Precise diagnostic message.
        category: Diagnostic category.
        severity: Diagnostic severity.
    """

    rule_id: str
    name: str
    line: int
    column: int
    message: str
    category: str = "markdown-conformance"
    severity: str = "warning"


@dataclass(frozen=True)
class MarkdownLine:
    """One Markdown source line.

    Attributes:
        number: One-based source line number.
        text: Raw line text without its newline character.
    """

    number: int
    text: str


@dataclass(frozen=True)
class MarkdownSource:
    """Minimal source context needed by conformance rules.

    Attributes:
        text: Full Markdown source text.
        lines: One-based source lines.
        path: Optional source path for local resource resolution.
        settings: Verification settings for this source.
    """

    text: str
    lines: tuple[MarkdownLine, ...]
    path: Path | None = None
    settings: VerificationSettings = field(default_factory=default_settings)

    @classmethod
    def from_text(
        cls,
        text: str,
        *,
        source_path: str | Path | None = None,
        settings: VerificationSettings | None = None,
    ) -> MarkdownSource:
        """Build source context from raw Markdown text.

        Args:
            text: Markdown source text.
            source_path: Optional source path for resource checks.
            settings: Verification settings for rule behavior.

        Returns:
            Markdown source context.
        """
        path = Path(source_path) if source_path is not None else None
        return cls(
            text=text,
            lines=tuple(
                MarkdownLine(number=index, text=line)
                for index, line in enumerate(text.splitlines(), start=1)
            ),
            path=path,
            settings=settings or default_settings(),
        )

    def rule_options(self, rule_id: str) -> dict[str, object]:
        """Return configured options for one rule.

        Args:
            rule_id: Rule identifier to read.

        Returns:
            Rule option mapping.
        """
        return self.settings.rule_options(rule_id)


type MarkdownRule = Callable[[MarkdownSource], tuple[Diagnostic, ...]]


@dataclass(frozen=True)
class MarkdownPolicy:
    """Policy describing which Markdown conformance rules apply.

    Attributes:
        name: Public policy name.
        rules: Ordered conformance rule callables.
    """

    name: str
    rules: tuple[MarkdownRule, ...]
