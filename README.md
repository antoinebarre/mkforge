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

Temporary outputs are created under `work/` and removed at the end of each
quality or packaging execution. The directory is kept in the repository with
`work/.gitkeep`.

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
            Table(
                headers=("Check", "Status"),
                rows=(
                    ("format", "pass"),
                    ("lint", "pass"),
                    ("tests", "pass"),
                ),
            ),
        ),
    ),
)

markdown = report.render()
```

## Markdown Linting

MkForge also exposes a markdownlint-inspired diagnostic API.

```python
from mkforge import lint_markdown

diagnostics = lint_markdown("# Title\n\ntext   \n")
```

Custom diagnostics can be added with `MarkdownLinter.register_rule()` and
`FunctionRule`.

## Relationship With Scribpy

MkForge is intended to be independent from Scribpy.

- `mkforge` generates Markdown reports from Python data.
- `scribpy` assembles and builds Markdown documentation projects.
- `uvforge` initializes and runs quality gates for Python packages using `uv`.

Scribpy and uvforge may depend on MkForge for generated reports, but MkForge
should not depend on either of them.
