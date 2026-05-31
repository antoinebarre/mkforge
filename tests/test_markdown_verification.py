"""Tests for Markdown and GFM verification."""

from pathlib import Path

import pytest

from mkforge import verify, verify_file
from mkforge.verification.profiles import MARKDOWN_PROFILE
from mkforge.verification.registry import (
    GFM_RULES,
    MARKDOWN_RULES,
    verification_rule_registry,
)
from tests.expectations import expect


def test_verification_registers_one_module_per_diagnostic() -> None:
    """Requirement: every verification diagnostic is a registered rule."""
    registry = verification_rule_registry()

    expect(len(registry.rules) == len(MARKDOWN_RULES + GFM_RULES), registry)
    expect("MKV001" in registry.rules, registry)
    expect("MKG001" in registry.rules, registry)


def test_markdown_profile_excludes_gfm_diagnostics() -> None:
    """Requirement: CommonMark verification is separate from GFM checks."""
    source = "# Title\n\nbare http://example.com\n| A | B |\n| - |\n"

    diagnostics = verify(source, profile=MARKDOWN_PROFILE)

    expect("MKG001" not in {item.rule_id for item in diagnostics}, diagnostics)
    expect("MKG003" not in {item.rule_id for item in diagnostics}, diagnostics)


def test_verification_reports_representative_diagnostics() -> None:
    """Requirement: verification reports syntax and GFM issues."""
    source = (
        "#Title\n"
        "# Title\n"
        "### Jump\n"
        "#Bad\n"
        "* a\n"
        "  * b\n"
        "1. one\n"
        "1. two\n"
        "Text   \n"
        "\tTab\n"
        "(foo)[bar]\n\n\n"
        "This line is long enough to cross the configured limit marker\n"
        "$ ls\n"
        "> quote\n> quote\n"
        "```py\nx\n```\n"
        "paragraph\n"
        "<div>\n"
        "---\n***\n"
        "* a *\n"
        "` code `\n"
        "[ text ](url)\n"
        "    indented\n"
        "~~~py\nx\n~~~\n"
        "*em* and _em_\n"
        "**strong** and __strong__\n"
        "[use][missing]\n"
        "[unused]: url\n"
        "bare http://example.com\n"
        "| A | B |\n| - |\n"
        "text| tail\n"
        "|x| y|\n"
    )

    diagnostics = verify(
        source,
        config={"MKV010": {"line_length": 40}},
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}

    expect("MKV012" in rule_ids, diagnostics)
    expect("MKV022" in rule_ids, diagnostics)
    expect("MKG001" in rule_ids, diagnostics)
    expect("MKG003" in rule_ids, diagnostics)


def test_verification_supports_files_config_and_disabled_rules(
    tmp_path: Path,
) -> None:
    """Requirement: file verification accepts config and disabled rules."""
    path = tmp_path / "sample.md"
    path.write_text("# Title\n\nshort\n", encoding="utf-8")

    diagnostics = verify_file(
        path,
        config={"MKV010": {"line_length": 3}},
        disabled={"MKV010"},
    )

    expect(not diagnostics, diagnostics)


def test_verification_rejects_unknown_profiles() -> None:
    """Requirement: unknown verification profiles fail clearly."""
    with pytest.raises(ValueError, match="unknown Markdown verification"):
        verification_rule_registry("unknown")
