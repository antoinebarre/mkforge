"""Factory function for building a RuleRegistry from rule module paths."""

from __future__ import annotations

from importlib import import_module

from mkforge.diagnostics.rules import FunctionRule, RuleRegistry


def load_rules(module_names: tuple[str, ...]) -> RuleRegistry:
    """Build a RuleRegistry by importing named rule modules.

    Each module must expose RULE_ID, NAME, and check attributes.

    Args:
        module_names: Fully qualified rule module names to import.

    Returns:
        Registry populated with one FunctionRule per module.
    """
    registry = RuleRegistry()
    for module_name in module_names:
        module = import_module(module_name)
        rule = FunctionRule(module.RULE_ID, module.NAME, module.check)
        registry.register(rule)
    return registry
