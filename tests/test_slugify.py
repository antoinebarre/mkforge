"""Tests for GitHub-style heading slugification."""

import pytest

from mkforge import slugify_heading


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "hello-world"),
        ("Analyse des Risques", "analyse-des-risques"),
        ("C'est l'été !", "c-est-l-été"),
        ("`code` inline", "code-inline"),
        ("  leading spaces  ", "leading-spaces"),
        ("A & B", "a-b"),
    ],
)
def test_slugify_heading_matches_github_anchor_algorithm(
    text: str,
    expected: str,
) -> None:
    """Requirement: slugs follow the GitHub Markdown anchor algorithm."""
    actual = slugify_heading(text)
    if actual != expected:
        raise AssertionError(actual)


def test_slugify_heading_preserves_unicode_letters() -> None:
    """Requirement: Unicode letters are case-folded, not transliterated."""
    actual = slugify_heading("Étude côté Réseau")
    expected = "étude-côté-réseau"
    if actual != expected:
        raise AssertionError(actual)


def test_slugify_heading_strips_inline_emphasis_markers() -> None:
    """Requirement: inline Markdown emphasis markers are removed."""
    actual = slugify_heading("**Bold** and _italic_ and ~~strike~~")
    expected = "bold-and-italic-and-strike"
    if actual != expected:
        raise AssertionError(actual)


def test_slugify_heading_collapses_repeated_punctuation() -> None:
    """Requirement: a run of non-alphanumeric characters yields one hyphen."""
    actual = slugify_heading("A  ,,,  B")
    expected = "a-b"
    if actual != expected:
        raise AssertionError(actual)


def test_slugify_heading_preserves_existing_hyphen_runs() -> None:
    """Requirement: literal hyphens in the input are not collapsed."""
    actual = slugify_heading("A---B")
    expected = "a---b"
    if actual != expected:
        raise AssertionError(actual)


def test_slugify_heading_accepts_blank_text() -> None:
    """Requirement: a blank heading slugifies to an empty string."""
    actual = slugify_heading("   ")
    if actual != "":
        raise AssertionError(actual)


def test_slugify_heading_rejects_non_string_input() -> None:
    """Requirement: non-string input raises TypeError."""
    with pytest.raises(TypeError):
        slugify_heading(123)  # type: ignore[arg-type]
