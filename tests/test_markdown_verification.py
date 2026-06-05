"""Tests for Markdown conformance verification policies."""

# ruff: noqa: SLF001

from pathlib import Path

from mkforge import (
    Diagnostic,
    MarkdownLine,
    MarkdownSource,
    VerificationReport,
    verify_markdown,
    verify_markdown_file,
)
from mkforge.verification.rules.markdown import markdownlint_remaining
from mkforge.verification.rules.markdown.mkf001_local_resource_exists import (
    _is_missing_local_target,
)
from mkforge.verification.settings import (
    VerificationSettings,
    _settings_files,
    _settings_root,
    _string_list,
    _verification_table,
    load_settings,
)
from tests.expectations import expect

CUSTOM_LINE_LENGTH = 120


def test_default_policy_merges_markdown_and_gfm_conformance() -> None:
    """Requirement: default verification runs Markdown and GFM diagnostics."""
    source = (
        "#Bad\n\n# Heading#\n\n| A | B |\n| -- | - |\n| one |\n- [y] task\n"
    )

    report = verify_markdown(source)
    rule_ids = {diagnostic.rule_id for diagnostic in report.diagnostics}

    expect(report.rule_set_name == "markdown-compliance", report)
    expect(
        {"MD018", "MD020", "GFM001", "GFM002", "GFM003"} <= rule_ids,
        report,
    )


def test_verification_report_passes_when_no_diagnostics() -> None:
    """Requirement: clean Markdown returns a passing report."""
    source = (
        "# Title\n\n| A | B |\n| --- | --- |\n| one | two |\n\n- [x] task\n"
    )

    report = verify_markdown(source)

    expect(isinstance(report, VerificationReport), report)
    expect(report.passed, report)
    expect(report.diagnostics == (), report)


def test_verify_markdown_file_resolves_local_resources(tmp_path: Path) -> None:
    """Requirement: file verification checks relative resource paths."""
    document = tmp_path / "doc.md"
    image = tmp_path / "image.png"
    image.write_bytes(b"png")
    document.write_text(
        "![ok](image.png)\n![missing](missing.png)\n",
        encoding="utf-8",
    )

    settings = VerificationSettings(disabled=frozenset({"MD041"}))
    report = verify_markdown_file(document, settings=settings)

    expect(len(report.diagnostics) == 1, report)
    expect(report.diagnostics[0].rule_id == "MKF001", report)
    expect("missing.png" in report.diagnostics[0].message, report)


def test_raw_source_skips_local_resource_checks() -> None:
    """Requirement: raw source without a path cannot check local resources."""
    report = verify_markdown(
        "![missing](missing.png)\n",
        settings=VerificationSettings(disabled=frozenset({"MD041"})),
    )

    expect(report.diagnostics == (), report)


def test_local_resource_check_ignores_non_file_targets(tmp_path: Path) -> None:
    """Requirement: resource checks ignore remote URLs and empty fragments."""
    document = tmp_path / "doc.md"
    source = "[remote](https://example.com/a.png)\n[fragment](#heading)\n"
    document.write_text(source, encoding="utf-8")

    settings = VerificationSettings(disabled=frozenset({"MD041"}))
    report = verify_markdown_file(document, settings=settings)

    expect(report.diagnostics == (), report)


def test_markdownlint_compliance_examples_emit_rule_ids() -> None:
    """Requirement: compliance-focused markdownlint examples are covered."""
    source = (
        "(wrong)[https://example.com]\n"
        "#Missing space\n"
        "#Closed missing#\n"
        "See http://example.com for details.\n"
        "Here is ** bold ** text.\n"
        "` code `\n"
        "[ text ](https://example.com)\n"
    )

    report = verify_markdown(source)
    rule_ids = {diagnostic.rule_id for diagnostic in report.diagnostics}

    expect(
        {"MD011", "MD018", "MD020", "MD034", "MD037", "MD038", "MD039"}
        <= rule_ids,
        report,
    )


def test_all_markdownlint_rules_can_emit_diagnostics() -> None:
    """Requirement: every markdownlint RULES.md rule is implemented."""
    source = _all_markdownlint_rule_source()

    report = verify_markdown(source)
    rule_ids = {diagnostic.rule_id for diagnostic in report.diagnostics}

    expect(
        rule_ids >= _MARKDOWNLINT_RULE_IDS,
        sorted(_MARKDOWNLINT_RULE_IDS - rule_ids),
    )


def test_settings_can_disable_rules() -> None:
    """Requirement: TOML settings can disable selected rule identifiers."""
    settings = VerificationSettings(disabled=frozenset({"MD018"}))

    report = verify_markdown("#Bad\n", settings=settings)
    rule_ids = {diagnostic.rule_id for diagnostic in report.diagnostics}

    expect("MD018" not in rule_ids, report)


def test_markdownlint_rule_options_cover_default_branches() -> None:
    """Requirement: markdownlint options alter rule behavior."""
    source = MarkdownSource.from_text("")
    consistent = VerificationSettings(rules={"MD046": {"style": "consistent"}})
    indented = VerificationSettings(rules={"MD046": {"style": "indented"}})
    filtered = VerificationSettings(
        rules={
            "MD010": {"ignore_code_blocks": True},
            "MD013": {"tables": False, "headings": False},
            "MD003": {"style": "setext_with_atx"},
            "MD004": {"style": "dash"},
        },
    )

    expect(markdownlint_remaining._first_line_heading(source) == (), source)
    expect(
        markdownlint_remaining._code_block_style(
            MarkdownSource.from_text("```txt\nx\n```\n", settings=consistent),
        )
        == (),
        consistent,
    )
    expect(
        markdownlint_remaining._code_block_style(
            MarkdownSource.from_text("```txt\nx\n```\n", settings=indented),
        )[0].rule_id
        == "MD046",
        indented,
    )
    expect(
        markdownlint_remaining._code_filtered_lines(
            MarkdownSource.from_text("```\n\t\n```\n", settings=filtered),
            "MD010",
            "ignore_code_blocks",
        )
        == (MarkdownLine(1, "```"),),
        filtered,
    )
    expect(
        not markdownlint_remaining._line_is_too_long(
            MarkdownSource.from_text("| " + ("x" * 90), settings=filtered),
            MarkdownLine(1, "| " + ("x" * 90)),
            80,
        ),
        filtered,
    )
    expect(
        not markdownlint_remaining._line_is_too_long(
            MarkdownSource.from_text("# " + ("x" * 90), settings=filtered),
            MarkdownLine(1, "# " + ("x" * 90)),
            80,
        ),
        filtered,
    )
    expect(
        markdownlint_remaining._heading_style_matches(
            "atx",
            3,
            "setext_with_atx",
        ),
        filtered,
    )
    expect(
        markdownlint_remaining._expected_unordered_mark("dash", ()) == "dash",
        filtered,
    )
    expect(
        markdownlint_remaining._expected_unordered_mark("sublist", ()) == "",
        filtered,
    )
    expect(
        markdownlint_remaining._blank_line_diagnostics(
            (
                MarkdownLine(1, "a"),
                MarkdownLine(2, "# H"),
                MarkdownLine(3, "b"),
            ),
            2,
            "MD022",
            "blank",
        ),
        filtered,
    )
    expect(
        not markdownlint_remaining._previous_line_is_list_item(
            (MarkdownLine(1, "- a"),),
            1,
        ),
        filtered,
    )


def test_mkforge_settings_file_overrides_rule_options(tmp_path: Path) -> None:
    """Requirement: .mkforge settings override markdownlint defaults."""
    settings_path = tmp_path / ".mkforge"
    settings_path.write_text(
        "[verification]\n"
        'disabled = ["MD034"]\n'
        "[verification.rules.MD013]\n"
        f"line_length = {CUSTOM_LINE_LENGTH}\n",
        encoding="utf-8",
    )
    document = tmp_path / "doc.md"
    document.write_text(
        "# Title\n\nSee http://example.com\n",
        encoding="utf-8",
    )

    settings = load_settings(document)
    report = verify_markdown_file(document)
    rule_ids = {diagnostic.rule_id for diagnostic in report.diagnostics}

    expect(
        settings.rule_options("MD013")["line_length"] == CUSTOM_LINE_LENGTH,
        settings,
    )
    expect("MD034" not in rule_ids, report)


def test_settings_discovery_handles_edge_cases(tmp_path: Path) -> None:
    """Requirement: settings discovery handles missing and malformed tables."""
    empty = tmp_path / "empty"
    empty.mkdir()
    expect(_settings_files(empty) == (), empty)
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool]\nmkforge = 'bad'\n", encoding="utf-8")

    expect(_settings_root(tmp_path) == tmp_path, tmp_path)
    expect(_verification_table({"tool": "bad"}, pyproject) == {}, pyproject)
    expect(
        _verification_table({"tool": {"mkforge": "bad"}}, pyproject) == {},
        pyproject,
    )
    expect(_string_list("MD001") == (), pyproject)


def test_compliance_rules_ignore_fenced_code_examples() -> None:
    """Requirement: Markdown examples inside fences are not verified."""
    source = (
        "# Title\n\n"
        "```markdown\n"
        "#Bad\n"
        "(wrong)[https://example.com]\n"
        "http://example.com\n"
        "```\n"
    )

    report = verify_markdown(source)

    expect(report.diagnostics == (), report)


def test_local_resource_helper_requires_source_path() -> None:
    """Requirement: direct local-resource checks require a source path."""
    source = MarkdownSource.from_text("[missing](missing.png)\n")

    missing = _is_missing_local_target(source, "missing.png")

    expect(not missing, source)


def test_custom_rules_are_appended_after_builtin_rules() -> None:
    """Requirement: custom rules run after built-in verification rules."""
    report = verify_markdown(
        "# Title\n",
        custom_rules=(_custom_rule,),
    )

    expect(report.diagnostics[0].rule_id == "ACME001", report)


def test_diagnostics_sort_by_position_then_rule_id() -> None:
    """Requirement: verification diagnostics have stable source ordering."""
    report = verify_markdown(
        "#Bad\n# Heading#\n",
        custom_rules=(_custom_rule,),
    )
    keys = [
        (diagnostic.line, diagnostic.column, diagnostic.rule_id)
        for diagnostic in report.diagnostics
    ]

    expect(keys == sorted(keys), report)


def test_markdown_source_numbers_lines_from_one() -> None:
    """Requirement: source context records one-based line numbers."""
    source = MarkdownSource.from_text("a\nb\n", source_path="doc.md")

    expect(source.path is not None, source)
    expect([line.number for line in source.lines] == [1, 2], source)


def _custom_rule(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return one custom diagnostic for policy extension tests.

    Args:
        source: Markdown source context.

    Returns:
        Custom diagnostic tuple.
    """
    return (
        Diagnostic(
            rule_id="ACME001",
            name="Custom",
            line=1 if source.lines else 0,
            column=1,
            message="Custom conformance diagnostic.",
        ),
    )


_MARKDOWNLINT_RULE_IDS = {
    "MD001",
    "MD002",
    "MD003",
    "MD004",
    "MD005",
    "MD006",
    "MD007",
    "MD009",
    "MD010",
    "MD011",
    "MD012",
    "MD013",
    "MD014",
    "MD018",
    "MD019",
    "MD020",
    "MD021",
    "MD022",
    "MD023",
    "MD024",
    "MD025",
    "MD026",
    "MD027",
    "MD028",
    "MD029",
    "MD030",
    "MD031",
    "MD032",
    "MD033",
    "MD034",
    "MD035",
    "MD036",
    "MD037",
    "MD038",
    "MD039",
    "MD040",
    "MD041",
    "MD046",
    "MD047",
}


def _all_markdownlint_rule_source() -> str:
    """Return source that triggers every markdownlint RULES.md rule.

    Returns:
        Markdown source with representative rule violations.
    """
    long_line = "This line is intentionally long " * 5
    return (
        "Intro before heading\n"
        "### Jump heading.\n"
        "Underlined duplicate\n"
        "====================\n"
        "#  Multiple space heading\n"
        "#Closed heading#\n"
        "#  Closed heading  #\n"
        "  # Indented heading\n"
        "# Duplicate\n"
        "# Duplicate\n"
        "* item\n"
        "+ mixed marker\n"
        "  * indented top level\n"
        "    * bad indent\n"
        "1. ordered\n"
        "3. wrong ordered\n"
        "-  too many marker spaces\n"
        "Trailing space   \n"
        "\tHard tab\n"
        "(wrong)[https://example.com]\n"
        "\n\n"
        f"{long_line}\n"
        "```sh\n"
        "$ ls\n"
        "$ pwd\n"
        "```\n"
        ">  blockquote spacing\n"
        "> quote one\n"
        "\n"
        "> quote two\n"
        "text before fence\n"
        "```\n"
        "code\n"
        "```\n"
        "text after fence\n"
        "paragraph before list\n"
        "- list without blanks\n"
        "paragraph after list\n"
        "<div>html</div>\n"
        "---\n"
        "***\n"
        "**Looks like heading**\n"
        "Here is ** bold ** text.\n"
        "` code `\n"
        "[ text ](https://example.com)\n"
        "    indented code block\n"
        "no final newline"
    )
