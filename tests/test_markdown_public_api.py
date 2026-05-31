"""Focused tests for the public Markdown diagnostic API."""

from mkforge import (
    Diagnostic,
    FunctionRule,
    RuleRegistry,
    SourceContext,
    Validator,
    Verifier,
)
from mkforge.validation.registry import validation_rule_registry
from mkforge.verification.registry import verification_rule_registry
from tests.expectations import expect


def test_diagnostic_exposes_category() -> None:
    """Requirement: diagnostics expose their diagnostic category."""
    diagnostic = Diagnostic("X", "Name", 1, 1, "message", "validation")
    expect(diagnostic.category == "validation", diagnostic)


def test_source_context_returns_empty_rule_config() -> None:
    """Requirement: missing rule configuration is an empty mapping."""
    context = SourceContext("", (), ())
    expect(context.rule_config("X") == {}, context)


def test_rule_registry_starts_empty() -> None:
    """Requirement: custom registries can start without built-in rules."""
    registry = RuleRegistry()
    expect(registry.enabled_rules(set()) == (), registry)


def test_function_rule_delegates_check() -> None:
    """Requirement: function rules delegate to their wrapped function."""
    rule = FunctionRule("X", "Name", _empty_check)
    expect(rule.check(SourceContext("", (), ())) == (), rule)


def test_verifier_can_use_custom_empty_registry() -> None:
    """Requirement: verifier accepts explicit registries."""
    verifier = Verifier(registry=RuleRegistry())
    expect(verifier.verify("# Title\n") == (), verifier)


def test_validator_can_use_custom_empty_registry() -> None:
    """Requirement: validator accepts explicit registries."""
    validator = Validator(RuleRegistry())
    expect(validator.validate("# Title\n") == (), validator)


def test_verification_registry_is_not_empty() -> None:
    """Requirement: verification registry exposes built-in rules."""
    registry = verification_rule_registry()
    expect(bool(registry.rules), registry)


def test_validation_registry_is_not_empty() -> None:
    """Requirement: validation registry exposes built-in rules."""
    registry = validation_rule_registry()
    expect(bool(registry.rules), registry)


def test_verifier_stores_profile_name() -> None:
    """Requirement: verifier stores the requested profile."""
    verifier = Verifier(profile="markdown")
    expect(verifier.profile == "markdown", verifier)


def test_registry_replaces_duplicate_rule_ids() -> None:
    """Requirement: registering the same rule id replaces the rule."""
    registry = RuleRegistry()
    registry.register(FunctionRule("X", "First", _empty_check))
    registry.register(FunctionRule("X", "Second", _empty_check))
    expect(registry.rules["X"].name == "Second", registry)


def test_registry_filters_disabled_rules() -> None:
    """Requirement: disabled rule identifiers are excluded."""
    registry = RuleRegistry()
    registry.register(FunctionRule("X", "Name", _empty_check))
    expect(registry.enabled_rules({"X"}) == (), registry)


def test_registry_orders_enabled_rules() -> None:
    """Requirement: enabled rules are returned in identifier order."""
    registry = RuleRegistry()
    registry.register(FunctionRule("B", "B", _empty_check))
    registry.register(FunctionRule("A", "A", _empty_check))
    expect(registry.enabled_rules(set())[0].rule_id == "A", registry)


def test_diagnostic_default_severity_is_warning() -> None:
    """Requirement: diagnostics default to warning severity."""
    diagnostic = Diagnostic("X", "Name", 1, 1, "message", "validation")
    expect(diagnostic.severity == "warning", diagnostic)


def test_custom_function_rule_identity_is_public() -> None:
    """Requirement: function rules expose rule id and name."""
    rule = FunctionRule("X", "Name", _empty_check)
    expect(rule.rule_id == "X", rule)


def test_empty_validator_returns_tuple() -> None:
    """Requirement: validator results are immutable tuples."""
    validator = Validator(RuleRegistry())
    expect(isinstance(validator.validate(""), tuple), validator)


def test_empty_verifier_returns_tuple() -> None:
    """Requirement: verifier results are immutable tuples."""
    verifier = Verifier(registry=RuleRegistry())
    expect(isinstance(verifier.verify(""), tuple), verifier)


def _empty_check(_context: SourceContext) -> tuple[Diagnostic, ...]:
    """Return no diagnostics for public API adapter tests."""
    return ()
