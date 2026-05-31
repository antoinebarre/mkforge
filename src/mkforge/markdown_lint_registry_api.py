"""Public registry contract for Markdown lint rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import MarkdownRule


@dataclass
class MarkdownRuleRegistry:
    """Mutable registry for Markdown lint rules."""

    rules: dict[str, MarkdownRule] = field(default_factory=dict)

    def register(self, rule: MarkdownRule) -> None:
        """Register or replace one rule.

        Args:
            rule: Rule implementation.
        """
        self.rules[rule.rule_id] = rule

    def enabled_rules(self, disabled: set[str]) -> tuple[MarkdownRule, ...]:
        """Return rules not present in the disabled set.

        Args:
            disabled: Disabled rule identifiers.

        Returns:
            Enabled rules sorted by identifier.
        """
        return tuple(
            self.rules[rule_id]
            for rule_id in sorted(self.rules)
            if rule_id not in disabled
        )
