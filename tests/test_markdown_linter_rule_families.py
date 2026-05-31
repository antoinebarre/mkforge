"""Tests for broad Markdown linter rule coverage."""

from mkforge.markdown_linter import lint_markdown
from tests.expectations import expect


def test_markdown_linter_reports_all_rule_families() -> None:
    """Requirement: every bundled diagnostic rule is executable."""
    diagnostics = lint_markdown(
        _all_rule_source(),
        config={
            "MD013": {"line_length": 10},
            "MD043": {"headings": ["# Required"]},
            "MD044": {"names": ["Python"]},
            "MD054": {"inline": False, "full": False},
        },
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
    missing = _expected_rule_ids().difference(rule_ids)
    expect(not missing, missing)


def _all_rule_source() -> str:
    """Return Markdown source containing representative rule violations."""
    return (
        "Intro\n=====\n\n# Title\n\n### Skipped!\n# Title\n"
        "##  Wide\n#Closed#\n#  Closed  #\n # Indented\n"
        ">  quote\n\n\n* item\n+ item\n - uneven\n   - nested\n"
        "1. one\n3. three\n-  wide\n\n> a\n\n> b\n\n***\n---\n\n"
        "**fake heading**\n\n```python\n$ ls\n```\ntext\n"
        "```python\nx\n```\ntext\n    indented\n~~~\ncode\n~~~\n\n"
        "<div>inline</div>\nhttp://example.com\n* spaced * and _other_\n"
        "**strong** and __other__\n` code `\n[ text ](target)\n"
        "[empty]()\n![](image.png)\n[here](target)\n[missing](#absent)\n"
        "[ref][missing]\n[used][used]\n[unused]: target\n[used]: target\n"
        "python should be capitalized.\n|a|b\n| - | - |\n|one|\na| b\n\n"
    )


def _expected_rule_ids() -> set[str]:
    """Return expected rule identifiers for the all-rule fixture."""
    return {
        "MD003",
        "MD004",
        "MD005",
        "MD007",
        "MD012",
        "MD014",
        "MD019",
        "MD020",
        "MD021",
        "MD023",
        "MD024",
        "MD027",
        "MD028",
        "MD029",
        "MD030",
        "MD031",
        "MD032",
        "MD033",
        "MD037",
        "MD038",
        "MD039",
        "MD040",
        "MD043",
        "MD044",
        "MD045",
        "MD046",
        "MD048",
        "MD049",
        "MD050",
        "MD051",
        "MD052",
        "MD053",
        "MD054",
        "MD055",
        "MD059",
        "MD060",
    }
