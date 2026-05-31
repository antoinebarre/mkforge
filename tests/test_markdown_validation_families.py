"""Tests for broad Markdown validation rule family coverage."""

from mkforge import validate
from mkforge.validation.registry import validation_rule_registry
from tests.expectations import expect


def test_validation_rule_families_have_representative_coverage() -> None:
    """Requirement: every content validation diagnostic can be emitted."""
    diagnostics = validate(
        _invalid_validation_source(),
        config=_config(),
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}

    expected = set(validation_rule_registry().rules)
    missing = sorted(expected - rule_ids)
    expect(expected <= rule_ids, missing)


def test_validation_covers_acceptance_branches() -> None:
    """Requirement: validation accepts matching optional content rules."""
    source = "# Required\n\n## Body\n"
    config = {"MKC008": {"headings": ["# Required"]}}

    diagnostics = validate(source, config=config)
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}

    expect("MKC008" not in rule_ids, diagnostics)


def _invalid_validation_source() -> str:
    """Return source that triggers validation rule families."""
    return (
        "intro\n"
        "# Title?\n"
        "# Other\n"
        "## Same\n"
        "## Same\n"
        "**Pseudo**\n"
        "```\nx\n```\n"
        "[empty]() and [missing](#absent) and [here](https://e.com)\n"
        "![](ok.png)\n"
        '<img src="x.png">\n'
        "text mkforge\n"
        "[inline](x) and [full][ref]\n"
        "[ref]: x\n"
    )


def _config() -> dict[str, dict[str, object]]:
    """Return validation rule configuration."""
    return {
        "MKC008": {"headings": ["# Required"]},
        "MKC009": {"names": ["MkForge"]},
        "MKC012": {"inline": False, "full": False},
    }
