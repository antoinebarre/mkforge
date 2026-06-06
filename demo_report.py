"""Complete MkForge demonstration report."""

from __future__ import annotations

import sys
from pathlib import Path

from mkforge import (
    BlockQuote,
    BulletList,
    Chapter,
    CodeBlock,
    HorizontalRule,
    Image,
    LineBreak,
    NumberedList,
    Paragraph,
    Report,
    Section,
    Table,
    Text,
)


def main() -> None:
    """Generate a complete Markdown report demonstration."""
    output_path = Path("work/demo_report.md")
    report = build_demo_report()
    report.save(output_path)
    _print_summary(output_path, report.render())


def build_demo_report() -> Report:
    """Build a comprehensive report using the public MkForge API.

    Returns:
        Demonstration report.
    """
    return Report(
        title="MkForge Demonstration Report",
        metadata=_metadata(),
        toc=True,
        auto_numbering=True,
    ).add(
        _executive_summary(),
        _quality_chapter(),
        _technical_appendix(),
    )


def _metadata() -> dict[str, object]:
    """Return free-form report metadata."""
    return {
        "title": "MkForge Demonstration Report",
        "author": "Antoine Barre",
        "version": "0.1.0",
        "status": "demo",
        "tags": ["markdown", "reporting", "automation", "quality"],
        "generated_by": "demo_report.py",
        "draft": False,
    }


def _executive_summary() -> Chapter:
    """Create the executive summary chapter.

    Returns:
        Summary chapter.
    """
    return Chapter("Executive Summary").add(
        Paragraph(
            (
                Text("MkForge builds "),
                Text("structured Markdown reports", style="bold"),
                Text(" from Python data without string assembly."),
                LineBreak(),
                Text("The output remains plain "),
                Text("GitHub Flavored Markdown", style="code"),
                Text("."),
            ),
        ),
        BlockQuote(
            "A report should be reproducible, readable, and easy to audit.",
        ),
        Section("Scope").add(
            BulletList(
                (
                    "Generate Markdown from typed Python objects.",
                    "Render frontmatter from a caller-provided dictionary.",
                    "Support tables, lists, code blocks, images, and quotes.",
                    "Keep runtime dependencies limited to stdlib modules.",
                ),
            ),
        ),
        Section("Out Of Scope").add(
            BulletList(
                (
                    "Building HTML or PDF artifacts.",
                    "Scanning documentation projects.",
                    "Executing CI quality gates.",
                ),
            ),
        ),
    )


def _quality_chapter() -> Chapter:
    """Create the quality evidence chapter.

    Returns:
        Quality chapter.
    """
    return Chapter("Quality Evidence").add(
        Section("Check Matrix").add(
            Table.from_columns(
                {
                    "Check": ("format", "ruff", "mypy", "pytest", "metrics"),
                    "Purpose": (
                        "Stable code style",
                        "Static lint rules",
                        "Strict typing",
                        "Behavior and coverage",
                        "Complexity and maintainability",
                    ),
                    "Expected": ("pass", "pass", "pass", "100%", "pass"),
                },
            ),
        ),
        Section("Risk Review").add(
            Paragraph(
                "The package is intentionally small. Most behavior is pure "
                "transformation from report objects to Markdown text.",
            ),
            NumberedList(
                (
                    "Validate user input when report objects are created.",
                    "Fail fast when unsupported children are added.",
                    "Keep renderer functions narrow and deterministic.",
                    "Verify public behavior through requirement tests.",
                ),
            ),
        ),
        HorizontalRule(),
        Section("Visual Placeholder").add(
            Image(
                "assets/quality-dashboard.png",
                alt="Quality dashboard placeholder",
                title="Demo image reference",
            ),
            Paragraph(
                "Image elements reference existing assets or URLs. The demo "
                "keeps the link as Markdown and does not copy files.",
            ),
        ),
    )


def _technical_appendix() -> Chapter:
    """Create the technical appendix chapter.

    Returns:
        Technical appendix chapter.
    """
    return Chapter("Technical Appendix").add(
        Section("Minimal Usage").add(
            CodeBlock(
                _usage_example(),
                language="python",
            ),
        ),
        Section("Nested Sections").add(
            Section("Level Three").add(
                Section("Level Four").add(
                    Paragraph(
                        "MkForge computes Markdown heading depth during "
                        "rendering, so stored titles stay unchanged.",
                    ),
                ),
            ),
        ),
        Section("Generated Artifact").add(
            Paragraph(
                (
                    Text("Running "),
                    Text("uv run python demo_report.py", style="code"),
                    Text(" writes "),
                    Text("work/demo_report.md", style="code"),
                    Text("."),
                ),
            ),
        ),
    )


def _usage_example() -> str:
    """Return a short code sample for the generated report.

    Returns:
        Python code sample.
    """
    return (
        "from mkforge import Chapter, Paragraph, Report\n"
        "\n"
        "report = Report(\n"
        '    title="Release Notes",\n'
        '    metadata={"title": "Release Notes", "draft": False},\n'
        "    toc=True,\n"
        ").add(\n"
        '    Chapter("Summary").add(\n'
        '        Paragraph("All checks passed."),\n'
        "    ),\n"
        ")\n"
        "\n"
        "markdown = report.render()"
    )


def _print_summary(output_path: Path, markdown: str) -> None:
    """Print a compact generation summary.

    Args:
        output_path: Markdown file written by the demo.
        markdown: Rendered Markdown content.
    """
    lines = (
        f"Wrote {output_path}",
        f"Characters: {len(markdown)}",
        "",
        markdown.splitlines()[0],
    )
    sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
