"""Tests for Markdown heading numbering helpers."""

from collections.abc import Callable
from typing import Any

import pytest

from mkforge import (
    renumber_markdown_headings,
    strip_heading_numbering_text,
    strip_markdown_heading_numbering,
)

_INVALID_TEXT: Any = 1
_INVALID_FIRST_NUMBER: Any = "1"
_INVALID_START_LEVEL: Any = "2"
_INVALID_BOOLEAN: Any = True
_INVALID_ZERO: Any = 0
_INVALID_HEADING_LEVEL: Any = 7


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Introduction", "Introduction"),
        ("1. Introduction", "Introduction"),
        ("1.2 Architecture", "Architecture"),
        ("1.2.3 - Design", "Design"),
        ("1.2.3. Design", "Design"),
        ("2026 Roadmap", "2026 Roadmap"),
        ("Version 2.0", "Version 2.0"),
    ],
)
def test_strip_heading_numbering_text_removes_heading_prefixes(
    text: str,
    expected: str,
) -> None:
    """Requirement: heading text numbering is stripped only at the start."""
    actual = strip_heading_numbering_text(text)
    if actual != expected:
        raise AssertionError(actual)


def test_strip_markdown_heading_numbering_updates_only_atx_headings() -> None:
    """Requirement: Markdown heading numbering is stripped outside fences."""
    markdown = (
        "# 1. Introduction\n"
        "\n"
        "## 1.3 Architecture\n"
        "\n"
        "```python\n"
        "# 1. This must not change\n"
        "```\n"
        "\n"
        "Text.\n"
    )
    expected = (
        "# Introduction\n"
        "\n"
        "## Architecture\n"
        "\n"
        "```python\n"
        "# 1. This must not change\n"
        "```\n"
        "\n"
        "Text.\n"
    )
    actual = strip_markdown_heading_numbering(markdown)
    if actual != expected:
        raise AssertionError(actual)


def test_strip_markdown_heading_numbering_preserves_non_heading_lines() -> (
    None
):
    """Requirement: lines that are not ATX headings remain unchanged."""
    markdown = "2026 Roadmap\nParagraph 1.2 stays.\nTitle\n=====\n"
    actual = strip_markdown_heading_numbering(markdown)
    if actual != markdown:
        raise AssertionError(actual)


def test_strip_markdown_heading_numbering_preserves_closed_atx_marker() -> (
    None
):
    """Requirement: closed ATX headings keep their closing marker."""
    markdown = "# 1. Title ###\n# ###\n#No heading\n"
    expected = "# Title ###\n# ###\n#No heading\n"
    actual = strip_markdown_heading_numbering(markdown)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_corrects_incoherent_numbering() -> None:
    """Requirement: renumbering recalculates heading numbers by hierarchy."""
    markdown = (
        "# 9. Introduction\n"
        "\n"
        "## 4. Mauvaise section\n"
        "\n"
        "### 8.7 Détail\n"
        "\n"
        "## Conclusion\n"
        "\n"
        "```markdown\n"
        "# 99. This must not change\n"
        "```\n"
    )
    expected = (
        "# 1. Introduction\n"
        "\n"
        "## 1.1. Mauvaise section\n"
        "\n"
        "### 1.1.1. Détail\n"
        "\n"
        "## 1.2. Conclusion\n"
        "\n"
        "```markdown\n"
        "# 99. This must not change\n"
        "```\n"
    )
    actual = renumber_markdown_headings(markdown)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_initializes_missing_parent_levels() -> (
    None
):
    """Requirement: renumbering preserves hierarchy when H2 appears first."""
    markdown = "## Child\r\n### Detail\r# Next"
    expected = "## 1.1. Child\r\n### 1.1.1. Detail\r# 2. Next"
    actual = renumber_markdown_headings(markdown)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_uses_custom_first_number() -> None:
    """Requirement: renumbering starts top-level headings at first_number."""
    markdown = "# Intro\n## Detail\n# Next\n"
    expected = "# 4. Intro\n## 4.1. Detail\n# 5. Next\n"
    actual = renumber_markdown_headings(markdown, first_number=4)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_uses_custom_missing_parent_number() -> (
    None
):
    """Requirement: missing parent heading levels start at first_number."""
    markdown = "## Detail\n### Leaf\n"
    expected = "## 4.1. Detail\n### 4.1.1. Leaf\n"
    actual = renumber_markdown_headings(markdown, first_number=4)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_uses_custom_start_level() -> None:
    """Requirement: renumbering starts at the requested heading level."""
    markdown = (
        "# 9. Document\n## 4. Titre 1\n### 8. Tritre niveau 2\n## Next\n"
    )
    expected = (
        "# Document\n## 1. Titre 1\n### 1.1. Tritre niveau 2\n## 2. Next\n"
    )
    actual = renumber_markdown_headings(markdown, start_level=2)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_combines_start_and_first_number() -> None:
    """Requirement: first_number applies at the configured start level."""
    markdown = "# Document\n## Titre 1\n### Titre niveau 2\n"
    expected = "# Document\n## 4. Titre 1\n### 4.1. Titre niveau 2\n"
    actual = renumber_markdown_headings(
        markdown,
        first_number=4,
        start_level=2,
    )
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_preserves_document_without_headings() -> (
    None
):
    """Requirement: documents without ATX headings remain unchanged."""
    markdown = "Paragraph.\n\n```markdown\n# 1. Still code\n```\n"
    actual = renumber_markdown_headings(markdown)
    if actual != markdown:
        raise AssertionError(actual)


@pytest.mark.parametrize(
    ("separator", "expected"),
    [
        (". ", "# 1. Title\n## 1.1. Child\n"),
        (" ", "# 1 Title\n## 1.1 Child\n"),
        (" - ", "# 1 - Title\n## 1.1 - Child\n"),
        ("", "# 1Title\n## 1.1Child\n"),
    ],
)
def test_renumber_markdown_headings_uses_requested_separator(
    separator: str,
    expected: str,
) -> None:
    """Requirement: renumbering separates number and title by separator."""
    markdown = "# Title\n## Child\n"
    actual = renumber_markdown_headings(markdown, separator=separator)
    if actual != expected:
        raise AssertionError(actual)


def test_renumber_markdown_headings_updates_h1_h2_h3_levels() -> None:
    """Requirement: renumbering follows H1, H2, and H3 hierarchy."""
    markdown = "# Top\n## Middle\n### Bottom\n## Next\n"
    expected = "# 1. Top\n## 1.1. Middle\n### 1.1.1. Bottom\n## 1.2. Next\n"
    actual = renumber_markdown_headings(markdown)
    if actual != expected:
        raise AssertionError(actual)


@pytest.mark.parametrize(
    "call",
    [
        lambda: strip_heading_numbering_text(_INVALID_TEXT),
        lambda: strip_markdown_heading_numbering(_INVALID_TEXT),
        lambda: renumber_markdown_headings(_INVALID_TEXT),
        lambda: renumber_markdown_headings("", separator=_INVALID_TEXT),
        lambda: renumber_markdown_headings(
            "",
            first_number=_INVALID_FIRST_NUMBER,
        ),
        lambda: renumber_markdown_headings("", first_number=_INVALID_BOOLEAN),
        lambda: renumber_markdown_headings(
            "",
            start_level=_INVALID_START_LEVEL,
        ),
        lambda: renumber_markdown_headings("", start_level=_INVALID_BOOLEAN),
    ],
)
def test_heading_numbering_helpers_reject_invalid_public_inputs(
    call: Callable[[], object],
) -> None:
    """Requirement: public helpers reject invalid input types."""
    with pytest.raises(TypeError):
        call()


def test_renumber_markdown_headings_rejects_invalid_first_number_value() -> (
    None
):
    """Requirement: renumbering rejects first_number values below one."""
    with pytest.raises(ValueError, match="first_number"):
        renumber_markdown_headings("", first_number=_INVALID_ZERO)


def test_renumber_markdown_headings_rejects_invalid_start_level_value() -> (
    None
):
    """Requirement: renumbering rejects start_level outside heading levels."""
    with pytest.raises(ValueError, match="start_level"):
        renumber_markdown_headings("", start_level=_INVALID_HEADING_LEVEL)
