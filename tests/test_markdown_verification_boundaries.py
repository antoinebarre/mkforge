"""Tests for Markdown verification parser boundary cases."""

from mkforge import verify
from tests.expectations import expect


def test_verification_accepts_fence_at_start() -> None:
    """Requirement: fences can appear at the beginning of a document."""
    diagnostics = verify("```python\n```\n")
    expect(not diagnostics, diagnostics)


def test_verification_reports_fence_at_file_end_newline() -> None:
    """Requirement: final newline rules still apply to trailing fences."""
    diagnostics = verify("# Title\n\n```python")
    rule_ids = {item.rule_id for item in diagnostics}
    expect("MKV030" in rule_ids, diagnostics)


def test_verification_accepts_setext_h1() -> None:
    """Requirement: setext level-1 headings are parsed."""
    diagnostics = verify("Title\n=====\n")
    rule_ids = {item.rule_id for item in diagnostics}
    expect("MKV002" not in rule_ids, diagnostics)


def test_verification_accepts_table_at_start() -> None:
    """Requirement: tables can appear at the beginning of a document."""
    diagnostics = verify("| A |\n| - |\n")
    rule_ids = {item.rule_id for item in diagnostics}
    expect("MKG004" not in rule_ids, diagnostics)
