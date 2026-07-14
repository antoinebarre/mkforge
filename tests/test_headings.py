"""Tests for public Markdown heading extraction."""

from dataclasses import FrozenInstanceError

import pytest

from mkforge import Heading, MarkdownSource, extract_headings
from tests.expectations import expect


def test_extract_headings_returns_atx_headings_in_document_order() -> None:
    """Requirement: public extraction returns ordered ATX headings."""
    source = MarkdownSource.from_text(
        "# Title\n\n"
        "Body\n\n"
        "### Deep Section ###\n\n"
        "Setext Title\n"
        "============\n"
        "## Next\n",
    )

    headings = extract_headings(source)

    expect(
        headings
        == (
            Heading(line=1, level=1, text="Title"),
            Heading(line=5, level=3, text="Deep Section"),
            Heading(line=9, level=2, text="Next"),
        ),
        headings,
    )


def test_extract_headings_ignores_fenced_code_blocks() -> None:
    """Requirement: public extraction skips ATX text inside fenced code."""
    source = MarkdownSource.from_text(
        "# Real\n\n"
        "```markdown\n"
        "# Hidden\n"
        "```\n\n"
        "~~~markdown\n"
        "## Also Hidden\n"
        "~~~\n\n"
        "## Visible\n",
    )

    headings = extract_headings(source)

    expect(
        headings
        == (
            Heading(line=1, level=1, text="Real"),
            Heading(line=11, level=2, text="Visible"),
        ),
        headings,
    )


def test_heading_is_frozen_public_dataclass() -> None:
    """Requirement: public Heading is frozen."""
    heading = Heading(line=3, level=2, text="Stable")

    with pytest.raises(FrozenInstanceError):
        Heading.__setattr__(heading, "text", "Changed")
