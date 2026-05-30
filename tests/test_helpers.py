"""Tests for report rendering helper behavior."""

from pathlib import Path

from mkforge import Chapter, Report
from mkforge.section_numbers import NumberingContext
from mkforge.table_of_contents import anchor_slug


def test_report_renders_metadata_without_tags() -> None:
    """Requirement: metadata renders caller-provided dictionary keys."""
    report = Report("Meta", metadata={"title": "Meta"})
    actual = report.render()
    expected = "---\ntitle: Meta\n---\n\n# Meta"
    if actual != expected:
        raise AssertionError(actual)


def test_report_save_creates_parent_directories(tmp_path: Path) -> None:
    """Requirement: save writes UTF-8 Markdown and creates parents."""
    output = tmp_path / "nested" / "report.md"
    Report("Saved").add(Chapter("Content")).save(output)
    actual = output.read_text(encoding="utf-8")
    if actual != "# Saved\n\n## Content":
        raise AssertionError(actual)


def test_helpers_cover_slug_and_numbering_edges() -> None:
    """Requirement: helpers expose deterministic slugs and numbering."""
    context = NumberingContext()
    context.enter_level()
    context.advance()
    context.enter_level()
    context.advance()
    expected = ("hello-2026", "1.1.")
    actual = (anchor_slug("Hello, 2026!"), context.prefix())
    if actual != expected:
        raise AssertionError(actual)
    context.leave_level()
    context.leave_level()
