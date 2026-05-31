"""Default Markdown content validation rule registry."""

from __future__ import annotations

from importlib import import_module

from mkforge.diagnostics import FunctionRule, RuleRegistry

VALIDATION_RULES = (
    "mkc001_duplicate_headings",
    "mkc002_single_title",
    "mkc003_heading_punctuation",
    "mkc004_emphasis_heading",
    "mkc005_code_language",
    "mkc006_first_line_title",
    "mkc007_empty_links",
    "mkc008_required_headings",
    "mkc009_proper_names",
    "mkc010_image_alt_text",
    "mkc011_link_fragments",
    "mkc012_link_style",
    "mkc013_descriptive_links",
)


def validation_rule_registry() -> RuleRegistry:
    """Return the default Markdown content validation registry.

    Returns:
        The default Markdown content validation registry.
    """
    registry = RuleRegistry()
    for module_name in _module_names():
        module = import_module(module_name)
        rule = FunctionRule(module.RULE_ID, module.NAME, module.check)
        registry.register(rule)
    return registry


def _module_names() -> tuple[str, ...]:
    """Return validation diagnostic module names.

    Returns:
        Validation diagnostic module names.
    """
    prefix = "mkforge.validation.rules"
    return tuple(f"{prefix}.{name}" for name in VALIDATION_RULES)
