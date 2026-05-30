"""Tests for package metadata."""

from mkforge import PROJECT_DESCRIPTION, PROJECT_NAME


def test_package_metadata() -> None:
    """Requirement: expose the MkForge package metadata identity."""
    expected = (
        "mkforge",
        "Programmatic Markdown report generation for Python.",
    )
    actual = (PROJECT_NAME, PROJECT_DESCRIPTION)
    if expected != actual:
        raise AssertionError(actual)
