"""Demonstrate MkForge Markdown validation helpers."""

# ruff: noqa: T201

from __future__ import annotations

from pathlib import Path

from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)


def main() -> None:
    """Run every public Markdown validation feature demo."""
    work_dir = Path("work/demo_validation")
    work_dir.mkdir(parents=True, exist_ok=True)
    _write_local_image(work_dir / "chart.png")

    markdown = _valid_markdown()
    missing_image_markdown = _missing_image_markdown()
    wrong_order_markdown = _wrong_order_markdown()
    wrong_yaml_markdown = _wrong_yaml_markdown()

    _print_intro()
    _show_yaml_validation(markdown, wrong_yaml_markdown)
    _show_chapter_validation(markdown, wrong_order_markdown)
    _show_local_image_validation(markdown, missing_image_markdown, work_dir)
    _show_remote_image_validation()
    _show_combined_gate(markdown, work_dir)


def _valid_markdown() -> str:
    """Return a Markdown document satisfying every validation contract.

    Returns:
        Markdown text with frontmatter, ordered H2 chapters, and one local
        image reference.
    """
    return (
        "---\n"
        "title: Validation Demo\n"
        "draft: false\n"
        "version: 1\n"
        "tags:\n"
        "  - validation\n"
        "  - markdown\n"
        "---\n\n"
        "# Validation Demo\n\n"
        "## Context\n\n"
        "This chapter explains the validation contract.\n\n"
        "### Scope\n\n"
        "Heading validation can check a precise level and title.\n\n"
        "![Chart](chart.png)\n\n"
        "## Architecture\n\n"
        "The document keeps validation separate from verification.\n\n"
        "## Tests\n\n"
        "The validation helpers return booleans for CI gates.\n"
    )


def _wrong_yaml_markdown() -> str:
    """Return Markdown with invalid frontmatter for the demo contract.

    Returns:
        Markdown text where ``draft`` is a string instead of a boolean.
    """
    return (
        "---\n"
        "title: Validation Demo\n"
        'draft: "false"\n'
        "---\n\n"
        "# Validation Demo\n"
    )


def _wrong_order_markdown() -> str:
    """Return Markdown with chapters in the wrong order.

    Returns:
        Markdown text whose H2 chapters do not match the expected sequence.
    """
    return (
        "# Validation Demo\n\n"
        "## Tests\n\n"
        "## Context\n\n"
        "## Architecture\n"
    )


def _missing_image_markdown() -> str:
    """Return Markdown referencing a missing local image.

    Returns:
        Markdown text containing an absent image target.
    """
    return "# Validation Demo\n\n![Missing](missing.png)\n"


def _write_local_image(path: Path) -> None:
    """Write a small demo image placeholder.

    Args:
        path: Local image path used by the validation demo.
    """
    path.write_bytes(b"demo image bytes")


def _print_intro() -> None:
    """Print the validation demo introduction."""
    print("\nMkForge Markdown validation demo")
    print("=" * 36)
    print("Validation answers project-specific yes/no questions.")
    print("It is separate from Markdown/GFM verification.")


def _show_yaml_validation(markdown: str, wrong_markdown: str) -> None:
    """Print YAML frontmatter validation examples.

    Args:
        markdown: Valid Markdown source.
        wrong_markdown: Markdown source with invalid frontmatter values.
    """
    minimum_contract = {"draft": False, "version": int}
    strict_contract = {
        "title": "Validation Demo",
        "draft": False,
        "version": 1,
        "tags": ["validation", "markdown"],
    }

    _print_section("1. YAML frontmatter validation")
    _show_result(
        "minimum contract: expected keys may be a subset",
        result=validate_markdown_yaml(markdown, minimum_contract),
    )
    _show_result(
        "strict contract: frontmatter keys must match exactly",
        result=validate_markdown_yaml(markdown, strict_contract, strict=True),
    )
    _show_result(
        'wrong type: string "false" does not satisfy boolean False',
        result=validate_markdown_yaml(wrong_markdown, {"draft": False}),
    )
    _show_result(
        "format-only check: expected bool accepts any boolean value",
        result=validate_markdown_yaml(markdown, {"draft": bool}),
    )


def _show_chapter_validation(markdown: str, wrong_markdown: str) -> None:
    """Print chapter order validation examples.

    Args:
        markdown: Valid Markdown source.
        wrong_markdown: Markdown source with H2 chapters in the wrong order.
    """
    _print_section("2. Chapter validation")
    _show_result(
        "minimum ordered contract: Context appears before Tests",
        result=validate_markdown_chapters(markdown, ("Context", "Tests")),
    )
    _show_result(
        "strict ordered contract: all H2 chapters must match exactly",
        result=validate_markdown_chapters(
            markdown,
            ("Context", "Architecture", "Tests"),
            strict=True,
        ),
    )
    _show_result(
        "heading contract: H2 Context then H3 Scope then H2 Architecture",
        result=validate_markdown_headings(
            markdown,
            ((2, "Context"), (3, "Scope"), (2, "Architecture")),
        ),
    )
    _show_result(
        "wrong heading level: Scope is H3, not H2",
        result=validate_markdown_headings(markdown, ((2, "Scope"),)),
    )
    _show_result(
        "wrong order: Tests before Context fails",
        result=validate_markdown_chapters(
            wrong_markdown,
            ("Context", "Tests"),
        ),
    )


def _show_local_image_validation(
    markdown: str,
    missing_markdown: str,
    work_dir: Path,
) -> None:
    """Print local image validation examples.

    Args:
        markdown: Markdown source with an existing local image.
        missing_markdown: Markdown source with a missing local image.
        work_dir: Directory used as the local image resolution root.
    """
    _print_section("3. Local image validation")
    _show_result(
        "existing local image: chart.png exists under work/demo_validation",
        result=validate_markdown_images(markdown, base_path=work_dir),
    )
    _show_result(
        "missing local image: missing.png does not exist",
        result=validate_markdown_images(missing_markdown, base_path=work_dir),
    )
    print("  base_path may be a directory or a Markdown file path.")
    print("  When base_path is a file, images resolve from its parent.")


def _show_remote_image_validation() -> None:
    """Print remote image validation examples."""
    remote_ok = (
        "# Remote image\n\n"
        "![Python logo](https://www.python.org/static/img/python-logo.png)\n"
    )
    remote_bad = "# Remote image\n\n![Bad](https://127.0.0.1/image.png)\n"

    _print_section("4. Remote image validation")
    _show_result(
        "public HTTP(S) URL: checked with HEAD then GET fallback",
        result=validate_markdown_images(remote_ok, timeout=3.0),
    )
    _show_result(
        "loopback/private hosts are rejected before network access",
        result=validate_markdown_images(remote_bad, timeout=3.0),
    )
    print(
        "  Remote checks depend on actual network access and server behavior.",
    )
    print("  Only HTTP and HTTPS URLs are contacted.")


def _show_combined_gate(markdown: str, work_dir: Path) -> None:
    """Print a combined CI-style validation gate.

    Args:
        markdown: Valid Markdown source.
        work_dir: Directory used for local image resolution.
    """
    valid = (
        validate_markdown_yaml(markdown, {"draft": False, "version": int})
        and validate_markdown_chapters(
            markdown,
            ("Context", "Architecture", "Tests"),
            strict=True,
        )
        and validate_markdown_headings(
            markdown,
            ((2, "Context"), (3, "Scope"), (2, "Architecture")),
        )
        and validate_markdown_images(markdown, base_path=work_dir)
    )

    _print_section("5. Combined validation gate")
    _show_result(
        "YAML contract + exact chapters + heading levels + local images",
        result=valid,
    )


def _print_section(title: str) -> None:
    """Print a demo section title.

    Args:
        title: Section title.
    """
    print(f"\n{title}")


def _show_result(label: str, *, result: bool) -> None:
    """Print one boolean validation result.

    Args:
        label: Human-readable validation scenario.
        result: Boolean validation result.
    """
    print(f"  {label}")
    print(f"    -> {result}")


if __name__ == "__main__":
    main()
