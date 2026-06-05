"""Demonstrate MkForge Markdown conformance verification features."""

# ruff: noqa: T201

from __future__ import annotations

from pathlib import Path

from mkforge import (
    Diagnostic,
    MarkdownRule,
    MarkdownSource,
    VerificationReport,
    VerificationSettings,
    verify_markdown,
    verify_markdown_file,
)


def main() -> None:
    """Run every public Markdown verification feature demo."""
    work_dir = Path("work/demo_verif")
    work_dir.mkdir(parents=True, exist_ok=True)

    _show_report(
        "1. Clean GFM source — passes the default merged policy",
        verify_markdown(_clean_gfm_source()),
    )
    _show_report(
        "2. Merged Markdown and GFM compliance violations",
        verify_markdown(_mixed_source()),
    )
    _show_report(
        "3. markdownlint-derived compliance examples",
        verify_markdown(_markdownlint_source()),
    )
    _show_report(
        "4. File verification with local resources",
        verify_markdown_file(_write_resource_demo(work_dir)),
    )
    _show_report(
        "5. Custom rule appended for one call",
        verify_markdown(
            "# Title\n\nBAD_MARKER\n",
            custom_rules=(_check_bad_marker,),
        ),
    )
    _show_report(
        "6. Disable specific rules via VerificationSettings",
        verify_markdown(
            "![missing](missing.png)\n",
            settings=VerificationSettings(disabled=frozenset({"MD041"})),
        ),
    )
    _show_report(
        "7. Custom rule options — stricter line length (40 chars)",
        verify_markdown(
            "# Title\n\nThis line is deliberately long enough to trigger MD013.\n",
            settings=VerificationSettings(
                rules={"MD013": {"line_length": 40}},
            ),
        ),
    )
    _show_report(
        "8. Multiple custom rules composed together",
        verify_markdown(
            "# Title\n\nBAD_MARKER\nTODO: remove\n",
            custom_rules=(_check_bad_marker, _check_todo),
        ),
    )
    _show_report(
        "9. source_path used without a real file (virtual path)",
        verify_markdown(
            "# Virtual document\n\nSee [link](#missing-anchor).\n",
            source_path="virtual/doc.md",
        ),
    )


def _clean_gfm_source() -> str:
    """Return Markdown that passes the default merged policy.

    Returns:
        Clean GFM source text.
    """
    return (
        "# Release Notes\n\n"
        "| Area | Status |\n"
        "| --- | --- |\n"
        "| Verification | ready |\n\n"
        "- [x] Markdown conformance\n"
        "- [ ] Future policy expansion\n"
    )


def _mixed_source() -> str:
    """Return Markdown with classic Markdown and GFM diagnostics.

    Returns:
        Markdown source containing representative conformance issues.
    """
    return (
        "#Bad heading\n\n"
        "# Closed heading#\n\n"
        "| Name | Status |\n"
        "| --- | - |\n"
        "| Parser |\n\n"
        "- [y] invalid task marker\n"
    )


def _markdownlint_source() -> str:
    """Return compliance-focused examples from markdownlint RULES.md.

    Returns:
        Markdown source containing markdownlint-derived compliance issues.
    """
    return (
        "(wrong)[https://example.com]\n"
        "See http://example.com for details.\n"
        "Here is ** bold ** text.\n"
        "` code `\n"
        "[ text ](https://example.com)\n"
    )


def _write_resource_demo(work_dir: Path) -> Path:
    """Create a Markdown file that references present and missing resources.

    Args:
        work_dir: Directory where demo files are written.

    Returns:
        Path to the Markdown file to verify.
    """
    image_path = work_dir / "present.png"
    document_path = work_dir / "resources.md"
    image_path.write_bytes(b"demo")
    document_path.write_text(
        "# Resources\n\n"
        "![present](present.png)\n"
        "![missing](missing.png)\n"
        "[remote](https://example.com/file.png)\n"
        "[fragment](#resources)\n",
        encoding="utf-8",
    )
    return document_path


def _check_bad_marker(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return a custom diagnostic for the demo-only BAD_MARKER token.

    Args:
        source: Markdown source context.

    Returns:
        Custom diagnostics for the demo marker.
    """
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        column = line.text.find("BAD_MARKER")
        if column >= 0:
            diagnostics.append(
                Diagnostic(
                    rule_id="DEMO001",
                    name="Demo marker",
                    line=line.number,
                    column=column + 1,
                    message="Remove the demo-only BAD_MARKER token.",
                ),
            )
    return tuple(diagnostics)


def _check_todo(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for lines containing a TODO comment marker.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each line that contains the TODO marker.
    """
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        column = line.text.find("TODO:")
        if column >= 0:
            diagnostics.append(
                Diagnostic(
                    rule_id="DEMO002",
                    name="Unresolved TODO",
                    line=line.number,
                    column=column + 1,
                    message="Resolve or remove this TODO before publishing.",
                ),
            )
    return tuple(diagnostics)


# Demonstrate that MarkdownRule is structurally compatible with any callable.
_rules_pipeline: tuple[MarkdownRule, ...] = (_check_bad_marker, _check_todo)


def _show_report(title: str, report: VerificationReport) -> None:
    """Print a compact verification report.

    Args:
        title: Demonstration section title.
        report: Verification report to display.
    """
    print(f"\n{title}")
    print(f"  rule set : {report.rule_set_name}")
    print(f"  passed   : {report.passed}")
    if not report.diagnostics:
        print("  (no diagnostics)")
        return
    print(f"  diagnostics ({len(report.diagnostics)}):")
    for diagnostic in report.diagnostics:
        _show_diagnostic(diagnostic)


def _show_diagnostic(diagnostic: Diagnostic) -> None:
    """Print one diagnostic line.

    Args:
        diagnostic: Diagnostic to display.
    """
    print(
        f"    [{diagnostic.rule_id}] "
        f"line {diagnostic.line}, col {diagnostic.column} — "
        f"{diagnostic.name}: {diagnostic.message}",
    )


if __name__ == "__main__":
    main()
