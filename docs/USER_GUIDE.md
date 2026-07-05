# MkForge User Guide

MkForge is a zero-dependency Python library for generating Markdown reports
from structured Python objects.

Use it when a script, quality gate, release job, audit task, or documentation
pipeline needs to produce reproducible Markdown without hand-built string
templates.

For exhaustive class, function, helper, rule, and feature contracts, see
[`API_REFERENCE.md`](API_REFERENCE.md).

## Contents

- [Install And Import](#install-and-import)
- [How To Think About MkForge](#how-to-think-about-mkforge)
- [Quick Start](#quick-start)
- [Classic Flows](#classic-flows)
  - [Flow 1: Generate A CI Quality Report](#flow-1-generate-a-ci-quality-report)
  - [Flow 2: Generate Release Notes](#flow-2-generate-release-notes)
  - [Flow 3: Build A Dependency Audit Report](#flow-3-build-a-dependency-audit-report)
  - [Flow 4: Save A Report With Local Images](#flow-4-save-a-report-with-local-images)
  - [Flow 5: Verify Markdown Before Publishing](#flow-5-verify-markdown-before-publishing)
  - [Flow 6: Validate A Project Document Contract](#flow-6-validate-a-project-document-contract)
  - [Flow 7: Use MkForge In A Documentation Pipeline](#flow-7-use-mkforge-in-a-documentation-pipeline)
- [Report Building Blocks](#report-building-blocks)
- [Rendering And Saving](#rendering-and-saving)
- [Frontmatter, TOC, And Numbering](#frontmatter-toc-and-numbering)
- [Verification](#verification)
- [Validation](#validation)
- [Heading Slugification](#heading-slugification)
- [Assets](#assets)
- [Errors](#errors)
- [Patterns And Recommendations](#patterns-and-recommendations)
- [Complete End-To-End Script](#complete-end-to-end-script)

## Install And Import

MkForge requires Python 3.12 or newer.

For development in this repository:

```bash
uv sync
```

Preferred imports come from the top-level `mkforge` package:

```python
from mkforge import Chapter, Paragraph, Report, Section, Table
```

For richer documents:

```python
from mkforge import (
    BlockQuote,
    BulletList,
    Chapter,
    CodeBlock,
    HorizontalRule,
    Image,
    LineBreak,
    Link,
    NumberedList,
    Paragraph,
    Report,
    Section,
    Table,
    Text,
)
```

For Markdown quality gates:

```python
from mkforge import (
    VerificationSettings,
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
    verify_markdown,
    verify_markdown_file,
)
```

For heading anchor slugs:

```python
from mkforge import slugify_heading
```

## How To Think About MkForge

MkForge has three jobs:

1. Build Markdown reports from typed Python objects.
2. Verify Markdown/GFM conformance and return diagnostics.
3. Validate project-specific content contracts and return booleans.

Those jobs are deliberately separate.

Generation answers: "What Markdown should this structured data produce?"

Verification answers: "Is this Markdown well-formed according to Markdown,
GitHub Flavored Markdown, and local resource rules?"

Validation answers: "Does this document contain the frontmatter, chapters,
headings, or images my project expects?"

The object model is small:

```text
Report
+-- Chapter
    +-- Section
    |   +-- Section
    |   +-- content element
    +-- content element
```

`Report` renders as one H1. `Chapter` renders as H2. `Section` renders as H3
through H6 depending on nesting depth.

Content elements render as Markdown blocks or inline fragments:

- `Paragraph`
- `Text`
- `LineBreak`
- `Link`
- `CodeBlock`
- `Table`
- `BulletList`
- `NumberedList`
- `Image`
- `HorizontalRule`
- `BlockQuote`

## Quick Start

```python
from mkforge import Chapter, Paragraph, Report, Section, Table

report = Report(
    title="Quality Report",
    metadata={"title": "Quality Report", "draft": False},
    toc=True,
).add(
    Chapter("Summary").add(
        Paragraph("All checks passed."),
        Table.from_columns(
            {
                "Check": ("format", "lint", "tests"),
                "Status": ("pass", "pass", "pass"),
            },
        ),
    ),
    Chapter("Details").add(
        Section("Test Runner").add(
            Paragraph("The suite completed with full coverage."),
        ),
    ),
)

markdown = report.render()
report.save("work/quality-report.md")
```

Rendered excerpt:

```markdown
---
title: Quality Report
draft: false
---

# Quality Report

- [Summary](#summary)
- [Details](#details)
  - [Test Runner](#test-runner)

## Summary

All checks passed.

| Check | Status |
| --- | --- |
| format | pass |
| lint | pass |
| tests | pass |
```

## Classic Flows

### Flow 1: Generate A CI Quality Report

This flow is useful in CI jobs that already ran formatters, linters, tests, or
coverage. MkForge receives the results and writes a Markdown artifact.

```python
from pathlib import Path

from mkforge import Chapter, CodeBlock, Paragraph, Report, Section, Table


def build_quality_report() -> Report:
    """Build a CI quality report from collected command results."""
    return Report(
        title="CI Quality Report",
        metadata={
            "title": "CI Quality Report",
            "status": "pass",
            "draft": False,
            "tags": ["ci", "quality"],
        },
        toc=True,
        auto_numbering=True,
    ).add(
        Chapter("Summary").add(
            Table(
                headers=("Check", "Status", "Detail"),
                rows=(
                    ("format", "pass", "0 files changed"),
                    ("ruff", "pass", "0 errors"),
                    ("pytest", "pass", "171 tests, 100% coverage"),
                ),
            ),
        ),
        Chapter("Evidence").add(
            Section("Test Command").add(
                CodeBlock("uv run pytest", language="sh"),
                Paragraph("The test suite completed successfully."),
            ),
        ),
    )


output = Path("work/reports/quality.md")
build_quality_report().save(output)
```

Typical use:

```bash
uv run python scripts/write_quality_report.py
```

Recommended contract:

- one `Summary` chapter for status;
- one `Evidence` or `Details` chapter for raw command output;
- `metadata["status"]` with `pass`, `fail`, or `warning`;
- `toc=True` when the report has more than two chapters.

### Flow 2: Generate Release Notes

Use this flow when release metadata already exists in Python data: version,
date, commit summaries, and compatibility notes.

```python
from mkforge import BulletList, Chapter, Paragraph, Report, Section


def build_release_notes(version: str, changes: tuple[str, ...]) -> Report:
    """Build release notes for a package version."""
    return Report(
        title=f"Release Notes {version}",
        metadata={
            "title": f"Release Notes {version}",
            "version": version,
            "draft": False,
            "tags": ["release"],
        },
        toc=True,
    ).add(
        Chapter("Highlights").add(
            BulletList(changes),
        ),
        Chapter("Upgrade Notes").add(
            Section("Compatibility").add(
                Paragraph("No breaking changes are expected for this release."),
            ),
            Section("Verification").add(
                Paragraph("The release was built after the full quality gate."),
            ),
        ),
    )


release = build_release_notes(
    "0.1.0",
    (
        "Added Markdown verification helpers.",
        "Added project-specific validation helpers.",
        "Improved report asset handling.",
    ),
)
release.save("work/release-notes-0.1.0.md")
```

Recommended validation after rendering:

```python
from mkforge import validate_markdown_chapters, validate_markdown_yaml

markdown = release.render()
ok = (
    validate_markdown_yaml(markdown, {"version": "0.1.0", "draft": False})
    and validate_markdown_chapters(
        markdown,
        ("Highlights", "Upgrade Notes"),
        strict=True,
    )
)
```

### Flow 3: Build A Dependency Audit Report

This flow is useful after tools such as `pip-audit`, `uv`, or internal package
inventory scripts produce structured results.

```python
from mkforge import Chapter, Paragraph, Report, Section, Table

VULNERABILITIES = (
    {
        "name": "example-lib",
        "version": "1.0.0",
        "advisory": "GHSA-0000",
        "fix": "1.0.1",
    },
)


def audit_table() -> Table:
    """Build a table from dependency audit findings."""
    if not VULNERABILITIES:
        return Table(("Package", "Version", "Advisory", "Fix"), ())

    return Table(
        headers=("Package", "Version", "Advisory", "Fix"),
        rows=tuple(
            (
                item["name"],
                item["version"],
                item["advisory"],
                item["fix"],
            )
            for item in VULNERABILITIES
        ),
    )


report = Report(
    title="Dependency Audit",
    metadata={"title": "Dependency Audit", "draft": False},
).add(
    Chapter("Summary").add(
        Paragraph(f"Findings: {len(VULNERABILITIES)}"),
    ),
    Chapter("Findings").add(
        Section("Known Vulnerabilities").add(audit_table()),
    ),
)
```

Recommended convention:

- generate an empty table with headers when no findings exist;
- keep raw scanner JSON outside the report unless humans need to read it;
- include exact fix versions when the scanner provides them.

### Flow 4: Save A Report With Local Images

Use `Image` when your report should reference charts, screenshots, or generated
figures.

```python
from pathlib import Path

from mkforge import Chapter, Image, Paragraph, Report, Section

chart_path = Path("work/charts/coverage.png")

report = Report("Coverage Report").add(
    Chapter("Coverage").add(
        Section("Trend").add(
            Image(chart_path, alt="Coverage trend"),
            Paragraph("The chart was generated by the coverage job."),
        ),
    ),
)

report.save("work/output/coverage.md", copy_assets=True)
```

When `copy_assets=True`, MkForge copies local images into an `assets/`
directory next to the Markdown output and rewrites links.

```text
work/output/
+-- assets/
|   +-- coverage.png
+-- coverage.md
```

Use this mode when the Markdown file will be uploaded, archived, or moved.

### Flow 5: Verify Markdown Before Publishing

Verification checks Markdown and GitHub Flavored Markdown conformance. It
returns diagnostics rather than raising for normal document issues.

```python
from mkforge import VerificationSettings, verify_markdown

settings = VerificationSettings(
    disabled=frozenset({"MD013"}),
)

report = verify_markdown(markdown, settings=settings)

if not report.passed:
    for diagnostic in report.diagnostics:
        print(
            f"{diagnostic.rule_id} "
            f"line {diagnostic.line}: {diagnostic.message}",
        )
    raise SystemExit(1)
```

Use this flow when:

- Markdown is generated by MkForge and should be checked before publishing;
- Markdown comes from another tool and must pass the same policy;
- CI should produce actionable rule IDs and line numbers.

### Flow 6: Validate A Project Document Contract

Validation checks your project rules: frontmatter values, chapter order,
heading sequence, and image existence.

```python
from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)

ok = (
    validate_markdown_yaml(markdown, {"draft": False, "version": str})
    and validate_markdown_chapters(
        markdown,
        ("Summary", "Findings", "Remediation"),
    )
    and validate_markdown_headings(
        markdown,
        ((2, "Summary"), (2, "Findings"), (2, "Remediation")),
    )
    and validate_markdown_images(markdown, base_path="work/report.md")
)
```

Use this flow when the document is syntactically valid Markdown, but your
project also requires specific content.

### Flow 7: Use MkForge In A Documentation Pipeline

MkForge does not build sites. It produces Markdown that another tool can
consume.

Typical flow:

1. Collect structured data in Python.
2. Build a `Report`.
3. Render or save Markdown.
4. Verify Markdown conformance.
5. Validate required project content.
6. Hand the Markdown file to MkDocs, Scribpy, GitHub, GitLab, or another
   documentation surface.

```python
from pathlib import Path

from mkforge import Chapter, Paragraph, Report, verify_markdown_file

output = Path("docs/generated/quality.md")
Report("Quality").add(
    Chapter("Summary").add(
        Paragraph("Generated during the documentation build."),
    ),
).save(output)

verification = verify_markdown_file(output)
if not verification.passed:
    raise SystemExit("Generated Markdown failed verification.")
```

## Report Building Blocks

### Report

`Report` is the root object. It renders as one H1 heading.

```python
Report(
    title="My Report",
    children=[],
    metadata=None,
    toc=False,
    auto_numbering=False,
)
```

Rules:

- `title` must be a non-empty string.
- `children` must be a list of `Chapter` objects.
- `metadata` must be `None` or a dictionary with string keys.
- `toc` and `auto_numbering` must be booleans.
- `Report.add()` accepts only `Chapter` objects.

### Chapter

`Chapter` renders as H2.

```python
Chapter("Summary").add(
    Paragraph("All checks passed."),
)
```

Rules:

- `title` must be a non-empty string.
- children may be content elements or `Section` objects.
- `Chapter.add()` returns the same chapter, enabling fluent construction.

### Section

`Section` renders as H3 through H6 depending on nesting depth.

```python
Chapter("Details").add(
    Section("Lint").add(
        Section("Ruff").add(
            Paragraph("No violations."),
        ),
    ),
)
```

Rules:

- sections can nest under chapters or other sections;
- nesting below H6 raises `ReportDepthError` during rendering;
- use chapters for major report phases and sections for details.

### Paragraph And Inline Elements

Use a string for simple paragraphs:

```python
Paragraph("All checks passed.")
```

Use a tuple for rich inline content:

```python
Paragraph(
    (
        Text("Status: "),
        Text("passed", style="bold"),
        Text(". See "),
        Link("https://example.com", text="details"),
        Text("."),
    ),
)
```

Supported `Text` styles:

- `plain`
- `bold`
- `italic`
- `code`
- `strikethrough`

Use `LineBreak()` inside a paragraph tuple when you need a Markdown hard line
break.

### CodeBlock

Use `CodeBlock` for command output, snippets, or configuration fragments.

```python
CodeBlock("uv run pytest\n171 passed", language="sh")
```

The language is optional but recommended when the consumer supports syntax
highlighting.

### Tables

Use `Table` when data is naturally row-oriented:

```python
Table(
    headers=("Check", "Status"),
    rows=(
        ("format", "pass"),
        ("tests", "pass"),
    ),
)
```

Use `Table.from_columns` when data is naturally column-oriented:

```python
Table.from_columns(
    {
        "Check": ("format", "tests"),
        "Status": ("pass", "pass"),
    },
)
```

Rules:

- headers must be a non-empty tuple of strings;
- each row must have the same number of cells as the headers;
- all columns passed to `from_columns` must have the same length.

### Lists

Use tuples, not lists:

```python
BulletList(("lint passed", "tests passed", "coverage passed"))
NumberedList(("collect evidence", "write report", "publish artifact"))
```

Empty list tuples are rejected because empty Markdown lists are not useful
report content.

### Images

Use `Image` for local files or remote image URLs:

```python
Image("assets/chart.png", alt="Coverage chart")
Image("https://example.com/chart.png", alt="Remote chart")
```

Local image existence is checked when saving. Remote images are downloaded only
when `copy_assets=True`.

### Quotes And Rules

Use `BlockQuote` for short callouts:

```python
BlockQuote("Generated by automation.\nReviewed by the release owner.")
```

Use `HorizontalRule` to separate sections inside a chapter:

```python
HorizontalRule()
```

## Rendering And Saving

### Render To A String

```python
markdown = report.render()
```

Rendering is deterministic and side-effect-free. It does not write files or
copy assets.

### Save To A File

```python
report.save("work/report.md")
```

Saving:

1. Validates local image paths.
2. Renders Markdown.
3. Creates parent directories when needed.
4. Writes UTF-8 text.

### Save And Bundle Assets

```python
report.save("work/report.md", copy_assets=True)
```

Saving with `copy_assets=True` additionally copies local images and downloads
allowed remote images into an `assets/` directory next to the output file.

## Frontmatter, TOC, And Numbering

### YAML Frontmatter

Pass `metadata` to prepend a YAML frontmatter block.

```python
Report(
    title="Audit",
    metadata={
        "title": "Audit",
        "version": "1.0.0",
        "draft": False,
        "tags": ["security", "release"],
        "reviewed": None,
    },
)
```

Supported values:

| Python value | Markdown frontmatter |
| --- | --- |
| `str` | string value |
| `int` or `float` | number text |
| `bool` | `true` or `false` |
| `None` | `null` |
| `list` or `tuple` | YAML sequence |

### Table Of Contents

Set `toc=True` to render a linked table of contents after the H1 heading.

```python
Report("Report", toc=True).add(
    Chapter("Summary"),
    Chapter("Details").add(
        Section("Logs"),
    ),
)
```

The TOC uses GitHub-style anchor slugs.

### Automatic Numbering

Set `auto_numbering=True` to number chapters and sections.

```python
Report("Report", auto_numbering=True).add(
    Chapter("Summary").add(
        Section("Status"),
    ),
)
```

Rendered headings:

```markdown
## 1. Summary

### 1.1. Status
```

## Verification

Verification checks Markdown conformance. It returns a `VerificationReport`.

```python
from mkforge import verify_markdown

verification = verify_markdown("# Title\n\nContent.\n")

if verification.passed:
    print("Markdown is clean.")
```

Diagnostics include:

| Field | Meaning |
| --- | --- |
| `rule_id` | Rule identifier such as `MD018` or `GFM001` |
| `name` | Human-readable rule name |
| `line` | 1-based line number |
| `column` | 1-based column number |
| `message` | Actionable diagnostic message |
| `category` | Diagnostic category |
| `severity` | Diagnostic severity |

### Verify A File

```python
from mkforge import verify_markdown_file

verification = verify_markdown_file("docs/report.md")
```

File verification can check local Markdown resources, including image and link
targets, relative to the file path.

### Disable Rules

```python
from mkforge import VerificationSettings, verify_markdown

settings = VerificationSettings(disabled=frozenset({"MD013"}))
verification = verify_markdown(markdown, settings=settings)
```

Use disabled rules sparingly. Prefer fixing generated Markdown when possible.

### Configure Rule Options

```python
settings = VerificationSettings(
    rules={"MD013": {"line_length": 120}},
)
verification = verify_markdown(markdown, settings=settings)
```

### Add A Custom Rule

```python
from mkforge import Diagnostic, MarkdownSource, verify_markdown


def reject_internal_marker(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Reject an internal marker before publishing."""
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        column = line.text.find("INTERNAL_ONLY")
        if column >= 0:
            diagnostics.append(
                Diagnostic(
                    rule_id="ACME001",
                    name="internal-marker",
                    line=line.number,
                    column=column + 1,
                    message="Remove INTERNAL_ONLY before publishing.",
                ),
            )
    return tuple(diagnostics)


verification = verify_markdown(
    markdown,
    custom_rules=(reject_internal_marker,),
)
```

Custom rules are useful for local publishing policy. They should not duplicate
built-in Markdown rules.

### Settings Files

`verify_markdown_file` can discover settings from `.mkforge`,
`.mkforge.toml`, or `[tool.mkforge.verification]` in `pyproject.toml`.

Example `.mkforge.toml`:

```toml
[verification]
disabled = ["MD013"]

[verification.rules.MD013]
line_length = 120
```

Example `pyproject.toml`:

```toml
[tool.mkforge.verification]
disabled = ["MD034"]

[tool.mkforge.verification.rules.MD013]
line_length = 120
```

## Validation

Validation checks content contracts and returns `True` or `False`.

Use validation after rendering or before accepting external Markdown.

### YAML Frontmatter

```python
from mkforge import validate_markdown_yaml

markdown = """---
title: Release Notes
draft: false
version: 3
tags:
  - release
  - docs
---

# Release Notes
"""

validate_markdown_yaml(markdown, {"draft": False})
validate_markdown_yaml(markdown, {"version": int})
```

Default mode is a minimum contract: extra keys are allowed.

Strict mode requires the complete frontmatter mapping to match:

```python
validate_markdown_yaml(
    markdown,
    {
        "title": "Release Notes",
        "draft": False,
        "version": 3,
        "tags": ["release", "docs"],
    },
    strict=True,
)
```

### Chapter Order

```python
from mkforge import validate_markdown_chapters

validate_markdown_chapters(
    markdown,
    ("Summary", "Findings", "Remediation"),
)
```

Default mode checks that expected H2 chapters appear in order. Other chapters
may appear between them.

Strict mode requires the complete H2 sequence:

```python
validate_markdown_chapters(
    markdown,
    ("Summary", "Findings", "Remediation"),
    strict=True,
)
```

### Heading Levels

```python
from mkforge import validate_markdown_headings

validate_markdown_headings(
    markdown,
    (
        (2, "Summary"),
        (3, "Status"),
        (2, "Findings"),
    ),
)
```

Use this when heading level is part of the contract.

### Images

```python
from mkforge import validate_markdown_images

validate_markdown_images(markdown, base_path="docs/report.md")
```

Local images resolve relative to `base_path`. If `base_path` is a file, images
resolve from the parent directory. Remote image checks contact only HTTP and
HTTPS URLs, and private or loopback hosts are rejected.

## Heading Slugification

Use `slugify_heading` to compute the GitHub-style anchor slug for a raw
heading title. This is useful when another tool needs to link into a
MkForge-generated document by heading text, for example `scribpy` assembling
several MkForge reports into one document and cross-linking between their
sections.

```python
from mkforge import slugify_heading

slugify_heading("Analyse des Risques")  # "analyse-des-risques"
slugify_heading("`code` inline")        # "code-inline"
```

Behavior:

- lowercases the heading text;
- strips inline Markdown markers (`` ` ``, `*`, `_`, `~`) before
  slugification;
- collapses any run of non-alphanumeric, non-hyphen characters into a single
  hyphen;
- trims leading and trailing hyphens;
- preserves Unicode letters such as accents, only case-folding them, never
  transliterating.

This matches the anchors GitHub generates for the same heading text, so a
link such as `[Analyse des Risques](#analyse-des-risques)` stays valid.

## Assets

MkForge treats image references carefully:

- construction accepts local paths and URLs;
- rendering keeps the path exactly as provided;
- saving validates local paths;
- `copy_assets=True` copies or downloads assets and rewrites image links.

Local asset example:

```python
from mkforge import Chapter, Image, Report

report = Report("Dashboard").add(
    Chapter("Screenshots").add(
        Image("work/screenshots/home.png", alt="Home dashboard"),
    ),
)

report.save("work/output/dashboard.md", copy_assets=True)
```

Remote asset notes:

- HTTP and HTTPS URLs are supported for remote image validation.
- Asset copying also permits supported remote schemes from the asset layer.
- Private and loopback addresses are blocked to reduce SSRF risk.
- Failed remote downloads raise `DownloadAssetError`.

## Errors

| Exception | Raised when |
| --- | --- |
| `InvalidChildError` | A container receives an unsupported child |
| `InvalidTableError` | A table has empty headers or mismatched rows |
| `ReportDepthError` | Section nesting would render below H6 |
| `MissingAssetError` | A local image path is missing during save |
| `DownloadAssetError` | A remote image cannot be downloaded |

Most construction errors are `TypeError` or `ValueError`. They are raised close
to the boundary so bad inputs fail early.

## Patterns And Recommendations

### Build Small Functions

Prefer small functions that return `Chapter`, `Section`, or content elements.

```python
def summary_chapter(status: str) -> Chapter:
    """Build the summary chapter."""
    return Chapter("Summary").add(
        Paragraph(f"Overall status: {status}."),
    )
```

This keeps report assembly readable:

```python
report = Report("Quality").add(
    summary_chapter("pass"),
    evidence_chapter(),
)
```

### Keep Data Separate From Presentation

Collect raw data first, then turn it into MkForge objects.

```python
rows = tuple((item.name, item.status) for item in checks)
table = Table(("Check", "Status"), rows)
```

This makes tests simpler and avoids mixing subprocess logic with report
composition.

### Use Tables For Dense Status

Use tables for repeated structured facts:

- checks and status;
- dependencies and versions;
- metrics and thresholds;
- files and diagnostics.

Use paragraphs for interpretation.

### Use Validation For Release Gates

A generated report can be valid Markdown but still miss a required chapter.
Use validation for those business rules.

```python
if not validate_markdown_chapters(markdown, ("Summary", "Risks"), strict=True):
    raise SystemExit("Report does not match the release contract.")
```

### Save After Verification When Possible

For generated Markdown, a useful sequence is:

1. Build the report.
2. Render Markdown.
3. Verify Markdown.
4. Validate project contracts.
5. Save the report.

If you need asset copying, save first, then verify the saved file with
`verify_markdown_file`.

## Complete End-To-End Script

This script builds a release quality report, verifies Markdown conformance,
validates project contracts, and saves the final artifact.

```python
from pathlib import Path

from mkforge import (
    BlockQuote,
    BulletList,
    Chapter,
    CodeBlock,
    HorizontalRule,
    Link,
    Paragraph,
    Report,
    Section,
    Table,
    Text,
    VerificationSettings,
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_yaml,
    verify_markdown,
)


def build_report() -> Report:
    """Build the release quality report."""
    return Report(
        title="Release Quality Report",
        metadata={
            "title": "Release Quality Report",
            "version": "0.1.0",
            "draft": False,
            "tags": ["release", "quality"],
        },
        toc=True,
        auto_numbering=True,
    ).add(
        Chapter("Summary").add(
            Paragraph(
                (
                    Text("Release status: "),
                    Text("ready", style="bold"),
                    Text("."),
                ),
            ),
            Table(
                headers=("Gate", "Status", "Detail"),
                rows=(
                    ("format", "pass", "0 files changed"),
                    ("lint", "pass", "0 violations"),
                    ("tests", "pass", "171 passed, 100% coverage"),
                ),
            ),
        ),
        Chapter("Evidence").add(
            Section("Commands").add(
                CodeBlock(
                    "make check\nmake check-dist",
                    language="sh",
                ),
            ),
            Section("Review Notes").add(
                BulletList(
                    (
                        "The package builds successfully.",
                        "The quality pipeline passes.",
                        "The distribution metadata is valid.",
                    ),
                ),
                BlockQuote("Release approval remains a human decision."),
            ),
        ),
        Chapter("Links").add(
            Paragraph(
                (
                    Text("Repository: "),
                    Link(
                        "https://github.com/antoinebarre/mkforge",
                        text="mkforge",
                    ),
                    Text("."),
                ),
            ),
            HorizontalRule(),
            Paragraph("Generated by MkForge."),
        ),
    )


def assert_quality(markdown: str) -> None:
    """Check Markdown conformance and project contracts."""
    verification = verify_markdown(
        markdown,
        settings=VerificationSettings(disabled=frozenset({"MD013"})),
    )
    if not verification.passed:
        for diagnostic in verification.diagnostics:
            print(
                f"{diagnostic.rule_id} "
                f"line {diagnostic.line}: {diagnostic.message}",
            )
        raise SystemExit(1)

    valid = (
        validate_markdown_yaml(
            markdown,
            {"version": "0.1.0", "draft": False},
        )
        and validate_markdown_chapters(
            markdown,
            ("Summary", "Evidence", "Links"),
        )
        and validate_markdown_headings(
            markdown,
            ((2, "1. Summary"), (2, "2. Evidence"), (2, "3. Links")),
        )
    )
    if not valid:
        raise SystemExit("Generated report does not match the contract.")


def main() -> None:
    """Generate and save the release quality report."""
    report = build_report()
    markdown = report.render()
    assert_quality(markdown)

    output = Path("work/release-quality-report.md")
    report.save(output)
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
```

Run the repository demos for smaller examples:

```bash
uv run python demo_report.py
uv run python demo_verif.py
uv run python demo_validation.py
```
