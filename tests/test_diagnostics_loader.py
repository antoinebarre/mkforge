"""Tests for the load_rules registry factory."""

from mkforge.diagnostics.loader import load_rules
from mkforge.verification.registry import GFM_RULES, MARKDOWN_RULES
from tests.expectations import expect


def test_load_rules_registers_all_markdown_rules() -> None:
    """Requirement: load_rules registers every module in MARKDOWN_RULES."""
    prefix = "mkforge.verification.rules.base"
    names = tuple(f"{prefix}.{name}" for name in MARKDOWN_RULES)
    registry = load_rules(names)
    expect(len(registry.rules) == len(MARKDOWN_RULES), registry.rules)


def test_load_rules_registers_all_gfm_rules() -> None:
    """Requirement: load_rules registers every module in GFM_RULES."""
    prefix = "mkforge.verification.rules.gfm"
    names = tuple(f"{prefix}.{name}" for name in GFM_RULES)
    registry = load_rules(names)
    expect(len(registry.rules) == len(GFM_RULES), registry.rules)


def test_load_rules_returns_empty_registry_for_empty_input() -> None:
    """Requirement: load_rules with no names returns an empty registry."""
    registry = load_rules(())
    expect(registry.enabled_rules(set()) == (), registry.rules)


def test_load_rules_assigns_rule_id_from_module() -> None:
    """Requirement: load_rules uses RULE_ID from each imported module."""
    names = ("mkforge.verification.rules.base.mkv001_heading_increment",)
    registry = load_rules(names)
    expect("MKV001" in registry.rules, registry.rules)


def test_load_rules_assigns_name_from_module() -> None:
    """Requirement: load_rules uses NAME from each imported module."""
    names = ("mkforge.verification.rules.base.mkv001_heading_increment",)
    registry = load_rules(names)
    rule = registry.rules["MKV001"]
    expect(isinstance(rule.name, str) and rule.name, rule)


def test_load_rules_later_module_overwrites_earlier_on_same_id() -> None:
    """Requirement: registering the same rule_id twice keeps the last entry."""
    name = "mkforge.verification.rules.base.mkv001_heading_increment"
    registry = load_rules((name, name))
    expect(len(registry.rules) == 1, registry.rules)
