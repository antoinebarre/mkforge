"""Tests for the Markdown linter."""

from pathlib import Path

from mkforge.markdown_lint_registry import (
    RULES,
    default_markdown_rule_registry,
)
from mkforge.markdown_linter import lint_markdown, lint_markdown_file
from tests.expectations import expect


def test_markdown_linter_registers_all_markdownlint_rule_ids() -> None:
    """Requirement: expose every diagnostic from markdownlint Rules.md."""
    registry = default_markdown_rule_registry()
    expected = tuple(rule_id for rule_id, _name, _check in RULES)
    actual = tuple(sorted(registry.rules))
    expect(actual == expected, actual)


def test_markdown_linter_reports_representative_diagnostics() -> None:
    """Requirement: emit clear diagnostics for Markdown rule violations."""
    source = (
        "# Title\n"
        "# Duplicate\n"
        "### Skipped!\n"
        "bad   \n"
        "[bad]()\n"
        "![](img.png)\n"
        "go here: https://example.com\n"
        "| A | B |\n"
        "| - | - |\n"
        "| only |\n"
    )
    diagnostics = lint_markdown(source)
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
    expected = {
        "MD001",
        "MD009",
        "MD025",
        "MD026",
        "MD034",
        "MD042",
        "MD045",
        "MD056",
    }
    expect(expected.issubset(rule_ids), rule_ids)


def test_markdown_linter_supports_config_disabled_and_files(
    tmp_path: Path,
) -> None:
    """Requirement: linter supports config, disabled rules, and file input."""
    path = tmp_path / "doc.md"
    path.write_text(
        "# Title\n\nThis line is deliberately long enough to fail.\n",
        encoding="utf-8",
    )
    diagnostics = lint_markdown_file(
        path,
        config={"MD013": {"line_length": 20}},
        disabled={"MD047"},
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
    expect("MD013" in rule_ids, rule_ids)
    expect("MD047" not in rule_ids, rule_ids)
