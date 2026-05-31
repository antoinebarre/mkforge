"""Tests for Markdown linter extension and rule breadth."""

from mkforge import FunctionRule, MarkdownDiagnostic, MarkdownLintContext
from mkforge.markdown_linter import MarkdownLinter, lint_markdown
from tests.expectations import expect


def test_markdown_linter_supports_custom_rules() -> None:
    """Requirement: public ICD allows custom diagnostic rules."""

    def check(context: MarkdownLintContext) -> tuple[MarkdownDiagnostic, ...]:
        """Return a custom diagnostic when marker text appears."""
        if "NEEDS_REVIEW" not in context.source:
            return ()
        return (
            MarkdownDiagnostic(
                "X001",
                "Custom marker",
                1,
                1,
                "Remove NEEDS_REVIEW marker.",
            ),
        )

    linter = MarkdownLinter()
    linter.register_rule(FunctionRule("X001", "Custom marker", check))
    diagnostics = linter.lint("# Title\n\nNEEDS_REVIEW\n")
    expect(
        "X001" in {diagnostic.rule_id for diagnostic in diagnostics},
        diagnostics,
    )


def test_markdown_linter_accepts_valid_document() -> None:
    """Requirement: valid Markdown produces no diagnostics."""
    valid = "# Title\n\nParagraph\n"
    expect(not lint_markdown(valid), valid)


def test_markdown_linter_parses_mixed_setext_documents() -> None:
    """Requirement: parser identifies setext and ATX heading styles."""
    setext = "Title\n=\n\n# Other\n\n```\n# ignored\n```\n"
    rule_ids = {diagnostic.rule_id for diagnostic in lint_markdown(setext)}
    expect("MD003" in rule_ids, rule_ids)


def test_markdown_linter_reports_empty_required_structure() -> None:
    """Requirement: required heading structure applies to empty files."""
    empty = lint_markdown("", config={"MD043": {"headings": ["# Required"]}})
    expect("MD043" in {diagnostic.rule_id for diagnostic in empty}, empty)


def test_markdown_linter_checks_blocks_at_start_of_file() -> None:
    """Requirement: block surround checks handle first-line blocks."""
    starts_with_list = lint_markdown("- item\nparagraph\n")
    expect(
        "MD032" in {diagnostic.rule_id for diagnostic in starts_with_list},
        starts_with_list,
    )


def test_markdown_linter_checks_blocks_at_end_of_file() -> None:
    """Requirement: block surround checks handle final-line blocks."""
    ends_with_list = lint_markdown("paragraph\n\n- item\n")
    expect(
        "MD032" not in {diagnostic.rule_id for diagnostic in ends_with_list},
        ends_with_list,
    )


def test_markdown_linter_checks_tables_at_start_of_file() -> None:
    """Requirement: table surround checks handle first-line tables."""
    starts_with_table = lint_markdown("| A |\nparagraph\n")
    expect(
        "MD058" in {diagnostic.rule_id for diagnostic in starts_with_table},
        starts_with_table,
    )


def test_markdown_linter_ignores_malformed_sequence_config() -> None:
    """Requirement: sequence-based rule config is defensive."""
    diagnostics = lint_markdown(
        "# Title\n\n[here](target)\n",
        config={
            "MD043": {"headings": object()},
            "MD044": {"names": object()},
            "MD059": {"prohibited_texts": object()},
        },
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
    expect("MD043" not in rule_ids, rule_ids)
    expect("MD044" not in rule_ids, rule_ids)
    expect("MD059" not in rule_ids, rule_ids)
