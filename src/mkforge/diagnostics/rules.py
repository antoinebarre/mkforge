"""Rule protocol and registry used by diagnostic engines."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from mkforge.diagnostics.models import Diagnostic, SourceContext


class Rule(Protocol):
    """Protocol implemented by diagnostic rules."""

    @property
    def rule_id(self) -> str:
        """Return the stable rule identifier.

        Returns:
            Stable diagnostic identifier used by reports and suppressions.
        """
        ...

    @property
    def name(self) -> str:
        """Return the human-readable rule name.

        Returns:
            Human-readable diagnostic name shown in reports.
        """
        ...

    def check(self, context: SourceContext) -> tuple[Diagnostic, ...]:
        """Return diagnostics for a parsed source context.

        Args:
            context: Parsed source context and rule configuration.

        Returns:
            Diagnostics emitted by this rule.
        """


type RuleCheck = Callable[[SourceContext], tuple[Diagnostic, ...]]


@dataclass(frozen=True)
class FunctionRule:
    """Function-backed diagnostic rule.

    Attributes:
        rule_id: Stable diagnostic identifier.
        name: Human-readable diagnostic name.
        check_function: Callable implementing the rule.
    """

    rule_id: str
    name: str
    check_function: RuleCheck

    def check(self, context: SourceContext) -> tuple[Diagnostic, ...]:
        """Return diagnostics emitted by the wrapped function.

        Args:
            context: Parsed source context and rule configuration.

        Returns:
            Diagnostics emitted by this rule.
        """
        return self.check_function(context)


@dataclass
class RuleRegistry:
    """Mutable registry for diagnostic rules.

    Attributes:
        rules: Registered rules keyed by rule identifier.
    """

    rules: dict[str, Rule] = field(default_factory=dict)

    def register(self, rule: Rule) -> None:
        """Register or replace one rule.

        Args:
            rule: Rule to register.
        """
        self.rules[rule.rule_id] = rule

    def enabled_rules(self, disabled: set[str]) -> tuple[Rule, ...]:
        """Return enabled rules sorted by identifier.

        Args:
            disabled: Rule identifiers to skip.

        Returns:
            Enabled rules sorted by rule identifier.
        """
        return tuple(
            self.rules[rule_id]
            for rule_id in sorted(self.rules)
            if rule_id not in disabled
        )
