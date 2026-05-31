"""Tests for broad Markdown diagnostic rule family coverage."""

from mkforge import verify
from mkforge.verification.registry import verification_rule_registry
from tests.expectations import expect


def test_verification_rule_families_have_representative_coverage() -> None:
    """Requirement: every verification diagnostic can be emitted."""
    source = (
        "#Title\n"
        "# Title\n"
        "### Jump\n"
        "#  Too many spaces\n"
        "# Closed#\n"
        "#  Closed  #\n"
        "  # Indented\n"
        "#Bad\n"
        "- item\n"
        "* item\n"
        "  - child\n"
        "   - wrong\n"
        "1. one\n"
        "1. two\n"
        "-  too\n"
        "Text   \n"
        "\tTab\n"
        "(foo)[bar]\n\n\n"
        "This line is long enough to cross the configured limit marker\n"
        ">  quote\n\n> quote\n"
        "```py\n$ ls\n```\n"
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
        "| one side\n"
        "|x| y|\n"
    )

    diagnostics = verify(
        source,
        config={"MKV010": {"line_length": 40}},
    )
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
    expected = set(verification_rule_registry().rules)
    expected.remove("MKV030")

    expect(expected <= rule_ids, sorted(expected - rule_ids))
    expect("MKV030" in {item.rule_id for item in verify("# T")}, [])
