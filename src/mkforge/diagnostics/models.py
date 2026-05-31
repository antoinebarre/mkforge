"""Data models shared by verification and validation diagnostics."""

from collections.abc import Mapping
from dataclasses import dataclass, field

type RuleConfig = Mapping[str, object]


@dataclass(frozen=True)
class Diagnostic:
    """One source diagnostic.

    Attributes:
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        line: One-based source line number.
        column: One-based source column number.
        message: Actionable diagnostic message.
        category: Diagnostic category such as verification or validation.
        severity: Diagnostic severity.
    """

    rule_id: str
    name: str
    line: int
    column: int
    message: str
    category: str
    severity: str = "warning"


@dataclass(frozen=True)
class Line:
    """One parsed source line.

    Attributes:
        number: One-based line number.
        text: Raw line text without a trailing newline.
        in_code: Whether the line is inside a fenced code block.
    """

    number: int
    text: str
    in_code: bool


@dataclass(frozen=True)
class Heading:
    """One parsed Markdown heading.

    Attributes:
        line: One-based source line number.
        level: Markdown heading level.
        text: Heading text without Markdown markers.
        style: Heading style name.
    """

    line: int
    level: int
    text: str
    style: str


@dataclass(frozen=True)
class SourceContext:
    """Parsed source passed to diagnostic rules.

    Attributes:
        source: Complete Markdown source text.
        lines: Parsed source lines.
        headings: Parsed Markdown headings.
        config: Per-rule configuration mapping.
    """

    source: str
    lines: tuple[Line, ...]
    headings: tuple[Heading, ...]
    config: Mapping[str, RuleConfig] = field(default_factory=dict)

    def rule_config(self, rule_id: str) -> RuleConfig:
        """Return configuration for a rule.

        Args:
            rule_id: Stable diagnostic identifier.

        Returns:
            Configuration mapping for the requested rule.
        """
        return self.config.get(rule_id, {})
