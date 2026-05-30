"""Tests for report rendering helper behavior."""

from mkforge import Metadata, Report
from mkforge.numbering import NumberingContext
from mkforge.toc import anchor_slug


def test_report_renders_metadata_without_tags() -> None:
    """Requirement: metadata renders scalar fields without empty tag lists."""
    report = Report("Meta", metadata=Metadata(title="Meta"))
    actual = report.render()
    expected = "---\ntitle: Meta\n---\n\n# Meta"
    if actual != expected:
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
