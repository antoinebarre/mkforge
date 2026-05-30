"""Tests for report model validation."""

import pytest

from mkforge import (
    BulletList,
    Chapter,
    InvalidChildError,
    InvalidTableError,
    NumberedList,
    Paragraph,
    Report,
    ReportDepthError,
    Section,
    Table,
)
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


def test_validation_rejects_invalid_content_data() -> None:
    """Requirement: content elements reject invalid construction data."""
    with pytest.raises(ValueError, match="Paragraph content"):
        Paragraph("")
    with pytest.raises(ValueError, match="BulletList"):
        BulletList(())
    with pytest.raises(ValueError, match="NumberedList"):
        NumberedList(())
    with pytest.raises(InvalidTableError):
        Table(())
    with pytest.raises(InvalidTableError):
        Table(("A", "B"), (("only one",),))


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
