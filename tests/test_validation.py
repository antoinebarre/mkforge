"""Tests for report model validation."""

from pathlib import Path

import pytest

from mkforge import (
    BulletList,
    Chapter,
    CodeBlock,
    Image,
    InvalidChildError,
    InvalidTableError,
    NumberedList,
    Paragraph,
    Report,
    ReportDepthError,
    Section,
    Table,
    Text,
)
from mkforge.headings import compute_section_heading_level
from mkforge.markdown import render_report, save_report
from mkforge.markdown_content import render_content


def test_validation_rejects_invalid_children() -> None:
    """Requirement: containers fail fast on unsupported child types."""
    invalid = Paragraph("not a chapter")
    with pytest.raises(InvalidChildError):
        Report("Invalid").add(invalid)  # type: ignore[arg-type]
    error = InvalidChildError("Report", "Paragraph")
    if str(error) != "Report cannot contain Paragraph.":
        raise AssertionError(error)
    with pytest.raises(InvalidChildError):
        Chapter("Invalid").add(object())  # type: ignore[arg-type]
    with pytest.raises(InvalidChildError):
        Section("Invalid").add(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Unknown node type"):
        render_content(object())


def test_validation_rejects_invalid_titles() -> None:
    """Requirement: report containers reject blank titles."""
    for factory in (Report, Chapter, Section):
        with pytest.raises(ValueError, match="title cannot be empty"):
            factory(" ")
    with pytest.raises(TypeError, match="Report title must be a string"):
        Report(1)  # type: ignore[arg-type]


def test_validation_rejects_invalid_content_data() -> None:
    """Requirement: content elements reject invalid construction data."""
    with pytest.raises(ValueError, match="Paragraph content"):
        Paragraph("")
    with pytest.raises(TypeError, match="Paragraph content must be a tuple"):
        Paragraph([Text("bad")])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Paragraph inline items"):
        Paragraph((object(),))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Text content must be a string"):
        Text(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Text style must be one of"):
        Text("bad", style="unknown")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="CodeBlock code must be a string"):
        CodeBlock(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="BulletList"):
        BulletList(())
    with pytest.raises(TypeError, match="BulletList items must be a tuple"):
        BulletList(["bad"])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="NumberedList"):
        NumberedList(())
    with pytest.raises(InvalidTableError):
        Table(())
    with pytest.raises(InvalidTableError):
        Table(("A", "B"), (("only one",),))
    with pytest.raises(TypeError, match="Table headers must be a tuple"):
        Table(["bad"])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Image path cannot be empty"):
        Image("")


def test_validation_rejects_too_deep_sections() -> None:
    """Requirement: rendering rejects section nesting beyond H6."""
    nested = Section("1").add(
        Section("2").add(
            Section("3").add(
                Section("4").add(
                    Section("5").add(
                        Section("6"),
                    ),
                ),
            ),
        ),
    )
    report = Report("Depth").add(Chapter("Root").add(nested))
    with pytest.raises(ReportDepthError):
        report.render()


def test_validation_rejects_invalid_metadata_and_paths(tmp_path: Path) -> None:
    """Requirement: metadata, render, and save errors are explicit."""
    with pytest.raises(TypeError, match="metadata must be a dict"):
        Report("Bad", metadata="bad")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="metadata keys must be a string"):
        Report("Bad", metadata={1: "bad"})  # type: ignore[dict-item]
    with pytest.raises(TypeError, match="Report toc must be a bool"):
        Report("Bad", toc="yes")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="report must be a Report"):
        render_report(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="save path cannot be empty"):
        save_report(Report("Bad"), "")
    with pytest.raises(TypeError, match="save path must be str or PathLike"):
        save_report(Report("Bad"), 1)  # type: ignore[arg-type]
    output = tmp_path / "ok.md"
    save_report(Report("Ok"), output)
    if output.read_text(encoding="utf-8") != "# Ok":
        raise AssertionError(output)


def test_validation_rejects_invalid_initial_children_and_depth() -> None:
    """Requirement: constructor children and depth inputs fail clearly."""
    with pytest.raises(TypeError, match="Report children must be a list"):
        Report("Bad", children=())  # type: ignore[arg-type]
    with pytest.raises(InvalidChildError):
        Report("Bad", children=[object()])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="Chapter children must be a list"):
        Chapter("Bad", children=())  # type: ignore[arg-type]
    with pytest.raises(InvalidChildError):
        Section("Bad", children=[object()])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="Section depth must be an int"):
        compute_section_heading_level("bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        compute_section_heading_level(0)
