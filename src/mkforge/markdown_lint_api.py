"""Public API contracts for the Markdown linter."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Protocol

from mkforge.markdown_lint_registry_api import MarkdownRuleRegistry

__all__ = ["MarkdownRuleRegistry"]

type RuleConfig = Mapping[str, object]


@dataclass(frozen=True)
class MarkdownDiagnostic:
    """One Markdown lint diagnostic.

    Attributes:
        rule_id: Markdown rule identifier.
        name: Human-readable rule name.
        line: One-based line number.
        column: One-based column number.
        message: Actionable diagnostic message.
        severity: Diagnostic severity.
    """

    rule_id: str
    name: str
    line: int
    column: int
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class MarkdownLine:
    """One source line with useful metadata.

    Attributes:
        number: One-based line number.
        text: Line text without the trailing newline.
        in_code: Whether the line is inside a fenced code block.
    """

    number: int
    text: str
    in_code: bool


@dataclass(frozen=True)
class MarkdownHeading:
    """Markdown heading discovered in a document.

    Attributes:
        line: One-based line number.
        level: Heading level.
        text: Heading text without marker syntax.
        style: Heading style label.
    """

    line: int
    level: int
    text: str
    style: str


@dataclass(frozen=True)
class MarkdownLintContext:
    """Parsed Markdown source passed to rules.

    Attributes:
        source: Original Markdown source.
        lines: Source lines with code fence state.
        headings: Parsed ATX headings.
        config: Rule-specific configuration.
    """

    source: str
    lines: tuple[MarkdownLine, ...]
    headings: tuple[MarkdownHeading, ...]
    config: Mapping[str, RuleConfig] = field(default_factory=dict)

    def rule_config(self, rule_id: str) -> RuleConfig:
        """Return configuration for a rule.

        Args:
            rule_id: Rule identifier.

        Returns:
            Rule configuration mapping.
        """
        return self.config.get(rule_id, {})


class MarkdownRule(Protocol):
    """Protocol implemented by Markdown lint rules."""

    @property
    def rule_id(self) -> str:
        """Return the stable rule identifier."""
        ...

    @property
    def name(self) -> str:
        """Return the human-readable rule name."""
        ...

    def check(
        self,
        context: MarkdownLintContext,
    ) -> tuple[MarkdownDiagnostic, ...]:
        """Return diagnostics for the given context.

        Args:
            context: Parsed Markdown source.

        Returns:
            Diagnostics emitted by the rule.
        """


type RuleCheck = Callable[
    [MarkdownLintContext],
    tuple[MarkdownDiagnostic, ...],
]


@dataclass(frozen=True)
class FunctionRule:
    """Function-backed Markdown lint rule."""

    rule_id: str
    name: str
    check_function: RuleCheck

    def check(
        self,
        context: MarkdownLintContext,
    ) -> tuple[MarkdownDiagnostic, ...]:
        """Return diagnostics emitted by this rule.

        Args:
            context: Parsed Markdown source.

        Returns:
            Diagnostics emitted by the wrapped function.
        """
        return self.check_function(context)
