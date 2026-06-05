"""Parametric sort-order tests for DiagnosticEngine."""

import pytest

from mkforge.diagnostics.engine import DiagnosticEngine
from mkforge.diagnostics.models import Diagnostic, SourceContext
from mkforge.diagnostics.parser import parse_markdown
from mkforge.diagnostics.rules import FunctionRule, RuleRegistry
from tests.expectations import expect


def _fixed_diagnostic(rule_id: str, line: int) -> Diagnostic:
    """Return a diagnostic at the given line number.

    Args:
        rule_id: Rule identifier to use.
        line: One-based line number.

    Returns:
        Diagnostic with the given rule identifier and line number.
    """
    return Diagnostic(rule_id, "Name", line, 1, "msg", "test")


def _rule_emitting(rule_id: str, line: int) -> FunctionRule:
    """Build a rule that always emits one diagnostic at a fixed line.

    Args:
        rule_id: Rule identifier to use.
        line: One-based line number for the emitted diagnostic.

    Returns:
        FunctionRule that emits one diagnostic.
    """

    def check(_: SourceContext) -> tuple[Diagnostic, ...]:
        """Return one fixed diagnostic.

        Args:
            _: Parsed source context (unused).

        Returns:
            Tuple containing one diagnostic.
        """
        return (_fixed_diagnostic(rule_id, line),)

    return FunctionRule(rule_id, "Name", check)


def _engine_with(*rules: FunctionRule) -> DiagnosticEngine:
    """Build a DiagnosticEngine from a sequence of rules.

    Args:
        *rules: FunctionRule instances to register.

    Returns:
        DiagnosticEngine with the given rules registered.
    """
    registry = RuleRegistry()
    for rule in rules:
        registry.register(rule)
    return DiagnosticEngine(registry, parse_markdown)


@pytest.mark.parametrize(
    ("rule_id_a", "line_a", "rule_id_b", "line_b", "first_id"),
    [
        ("T002", 1, "T001", 1, "T001"),
        ("T001", 2, "T002", 1, "T002"),
    ],
)
def test_engine_sort_order(
    rule_id_a: str,
    line_a: int,
    rule_id_b: str,
    line_b: int,
    first_id: str,
) -> None:
    """Requirement: sort order is (line, column, rule_id).

    Args:
        rule_id_a: First rule identifier.
        line_a: Line number for first rule diagnostic.
        rule_id_b: Second rule identifier.
        line_b: Line number for second rule diagnostic.
        first_id: Expected rule_id of the first sorted diagnostic.
    """
    engine = _engine_with(
        _rule_emitting(rule_id_a, line_a),
        _rule_emitting(rule_id_b, line_b),
    )
    result = engine.run("# Title\n\nLine\n")
    expect(result[0].rule_id == first_id, result)
