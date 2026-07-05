# MkForge

Programmatic Markdown report generation for Python.

MkForge is a small Python toolkit for building structured, reproducible
Markdown reports from code.

It provides composable report primitives such as sections, paragraphs, tables,
figures, metadata, checksums, and renderers so automation scripts can produce
readable Markdown artifacts without hand-written string assembly.

## Use Cases

- Quality gate reports
- CI and release summaries
- Code metrics reports
- Dependency audit reports
- Generated technical appendices
- Reproducible Markdown artifacts for documentation pipelines

## Scope

MkForge focuses on generating Markdown documents from structured Python data.

It is not:

- a Markdown project compiler;
- a static site generator;
- a CI runner;
- a replacement for documentation tools such as MkDocs.

Those tools can use MkForge as their reporting layer.

## Installation

```bash
uv sync
```

## Development

```bash
make check
```

`make check` runs formatting, Ruff, Flake8, docstring checks, Mypy, code
metrics, security checks, tests, and 100% coverage validation.

For CI-style non-mutating checks:

```bash
make ci
```

For package validation before publishing:

```bash
make check-dist
```

Temporary quality reports are written under `work/reports/`. Packaging checks
build distributions under `work/dist/`. The `work/` directory is kept in the
repository with `work/.gitkeep`.

## Example

```python
from mkforge import Chapter, Paragraph, Report, Section, Table

report = Report(
    title="Quality Report",
    metadata={"title": "Quality Report", "tags": ["quality", "ci"]},
    toc=True,
).add(
    Chapter("Summary").add(
        Section("Checks").add(
            Paragraph("All checks passed."),
            Table.from_columns(
                {
                    "Check": ("format", "lint", "tests"),
                    "Status": ("pass", "pass", "pass"),
                },
            ),
        ),
    ),
)

markdown = report.render()
```

## Markdown Verification

```python
from mkforge import verify_markdown

report = verify_markdown("# Title\n\n| A | B |\n| --- | --- |\n")
```

Verification covers pure Markdown and GitHub Flavored Markdown conformance in a
single pass. Custom rule callables can be appended for one verification call
without mutating the built-in policy.

## Markdown Validation

```python
from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)

ok = (
    validate_markdown_yaml(markdown, {"draft": False})
    and validate_markdown_chapters(markdown, ("Summary", "Details"))
    and validate_markdown_headings(markdown, ((2, "Summary"), (3, "Checks")))
    and validate_markdown_images(markdown, base_path="docs/report.md")
)
```

Validation answers project-specific boolean questions: expected YAML
frontmatter, required H2 chapters in order, heading level/title sequences, and
local or HTTP(S) image existence. Use `strict=True` for exact YAML keys or exact
heading and chapter sequences.

Runnable demos:

```bash
uv run python demo_report.py
uv run python demo_verif.py
uv run python demo_validation.py
```

## Relationship With Scribpy

MkForge is intended to be independent from Scribpy.

- `mkforge` generates Markdown reports from Python data.
- `scribpy` assembles and builds Markdown documentation projects.
- `yggtools` initializes and runs quality gates for Python packages using `uv`.

Scribpy and yggtools may depend on MkForge for generated reports, but MkForge
should not depend on either of them.
