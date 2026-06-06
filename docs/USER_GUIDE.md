# MkForge User Guide

MkForge is a zero-dependency Python library for building structured Markdown
reports programmatically. You compose a tree of typed objects, then call
`.render()` or `.save()` — the library handles all Markdown formatting.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Document Tree](#document-tree)
  - [Report](#report)
  - [Chapter](#chapter)
  - [Section](#section)
  - [Nesting rules](#nesting-rules)
- [Content Elements](#content-elements)
  - [Paragraph](#paragraph)
  - [Text](#text)
  - [LineBreak](#linebreak)
  - [Link](#link)
  - [CodeBlock](#codeblock)
  - [Table](#table)
  - [BulletList and NumberedList](#bulletlist-and-numberedlist)
  - [Image](#image)
  - [HorizontalRule](#horizontalrule)
  - [BlockQuote](#blockquote)
- [Rendering](#rendering)
  - [Render to string](#render-to-string)
  - [Save to file](#save-to-file)
  - [Asset management](#asset-management)
- [Report Options](#report-options)
  - [YAML frontmatter](#yaml-frontmatter)
  - [Table of contents](#table-of-contents)
  - [Automatic heading numbering](#automatic-heading-numbering)
- [Markdown Verification](#markdown-verification)
  - [Verify a string](#verify-a-string)
  - [Verify a file](#verify-a-file)
  - [VerificationReport](#verificationreport)
  - [Diagnostic fields](#diagnostic-fields)
  - [Disabling rules](#disabling-rules)
  - [Custom rules](#custom-rules)
  - [TOML settings](#toml-settings)
- [Error Reference](#error-reference)
- [Complete Example](#complete-example)

---

## Installation

```
uv sync
```

MkForge requires Python 3.12+ and has **no external dependencies**.

---

## Quick Start

```python
from mkforge import (
    BulletList, Chapter, CodeBlock, Paragraph,
    Report, Section, Table, Text,
)

report = (
    Report(title="Quality Report")
    .add(
        Chapter("Summary").add(
            Paragraph("All checks passed."),
            Table(
                headers=("Check", "Result"),
                rows=(
                    ("lint", "pass"),
                    ("tests", "pass"),
                    ("coverage", "100 %"),
                ),
            ),
        ),
        Chapter("Details").add(
            Section("Linting").add(
                Paragraph((
                    Text("Tool: "),
                    Text("ruff", style="code"),
                )),
                BulletList(("No violations found.",)),
            ),
            Section("Tests").add(
                CodeBlock("pytest --tb=short", language="sh"),
            ),
        ),
    )
)

print(report.render())
report.save("output/quality_report.md")
```

Output (excerpt):

```markdown
# Quality Report

## Summary

All checks passed.

| Check | Result |
| --- | --- |
| lint | pass |
| tests | pass |
| coverage | 100 % |

## Details

### Linting

Tool: `ruff`

- No violations found.

### Tests

```sh
pytest --tb=short
` `` `
```

---

## Document Tree

Reports follow a strict containment hierarchy:

```
Report
└── Chapter (H2)  ─ one or more
    ├── Section (H3–H6)  ─ zero or more, nestable
    │   ├── Section (H4)
    │   │   └── Section (H5)
    │   │       └── Section (H6)  ← deepest allowed
    └── <content element>  ─ Paragraph, Table, CodeBlock, …
```

### Report

`Report` is the root. It renders as an H1 heading.

```python
Report(
    title="My Report",            # required, non-empty string
    children=[],                  # optional initial Chapter list
    metadata=None,                # optional dict → YAML frontmatter
    toc=False,                    # include table of contents
    auto_numbering=False,         # prefix headings with 1., 1.1., …
)
```

`Report.add(*chapters)` appends `Chapter` objects and returns `self`
(fluent API). Only `Chapter` instances are accepted; any other type
raises `InvalidChildError`.

### Chapter

`Chapter` renders as an H2 heading. It may contain `Section` objects
and any content element.

```python
Chapter(
    title="Introduction",         # required, non-empty string
    children=[],                  # optional initial children list
)
```

`Chapter.add(*items)` accepts `Section` or any content element.

### Section

`Section` renders as H3 through H6 depending on nesting depth.
Depth is computed automatically from position in the tree:

| Depth below Chapter | Heading level |
| --- | --- |
| 1 | H3 |
| 2 | H4 |
| 3 | H5 |
| 4 | H6 |

```python
Section(
    title="Background",           # required, non-empty string
    children=[],                  # optional initial children list
)
```

`Section.add(*items)` accepts nested `Section` or any content element.

### Nesting rules

- A `Report` only accepts `Chapter` children.
- A `Chapter` or `Section` accepts `Section` or any content element.
- Nesting a `Section` more than 4 levels below a `Chapter` raises
  `ReportDepthError` at render time (H7 does not exist in Markdown).
- Passing the wrong type raises `InvalidChildError` immediately.

---

## Content Elements

All content elements are **frozen dataclasses** — immutable after
construction. Validation runs in `__post_init__` and raises immediately
on bad input.

### Paragraph

A block of text. The `content` argument is either a plain string or a
tuple of `Text`, `LineBreak`, and `Link` inline elements.

```python
# Plain string
Paragraph("All tests passed.")

# Inline elements
Paragraph((
    Text("Status: "),
    Text("passing", style="bold"),
    Text("."),
))
```

- A plain-string paragraph renders as-is.
- An inline-element paragraph renders as the concatenation of each
  element's `.render()` output.
- Empty strings are rejected with `ValueError`.

### Text

Inline text with an optional style.

```python
Text("hello")                          # plain (default)
Text("hello", style="bold")            # **hello**
Text("hello", style="italic")          # *hello*
Text("hello", style="code")            # `hello`
Text("hello", style="strikethrough")   # ~~hello~~
```

Valid styles: `"plain"` · `"bold"` · `"italic"` · `"code"` ·
`"strikethrough"`.

An empty string is accepted (renders as an empty inline span). An
unknown style raises `ValueError`.

### LineBreak

A GFM hard line break — two trailing spaces followed by a newline.
Use it inside a `Paragraph` tuple to force a new line without starting
a new block.

```python
Paragraph((
    Text("Line one."),
    LineBreak(),
    Text("Line two."),
))
```

### Link

An inline hyperlink.

```python
Link(url="https://example.com")                          # [](url)
Link(url="https://example.com", text="Example")          # [Example](url)
Link(url="https://example.com", text="Ex", title="Tip")  # [Ex](url "Tip")
```

- `url` is required and must be non-empty.
- `text` and `title` are optional and may be empty strings.

Use `Link` inside a `Paragraph` tuple:

```python
Paragraph((
    Text("See "),
    Link("https://example.com", text="the docs"),
    Text(" for details."),
))
```

### CodeBlock

A fenced code block with an optional language hint for syntax
highlighting.

```python
CodeBlock("x = 1 + 2")                    # plain fence
CodeBlock("x = 1 + 2", language="python") # ```python fence
CodeBlock("", language="sh")              # empty body is valid
```

Renders as:

```
```python
x = 1 + 2
` ``
```

### Table

A GFM pipe table. `headers` is required and must be a non-empty tuple
of strings. `rows` is optional; each row must be a tuple with the same
length as `headers`.

```python
Table(
    headers=("Name", "Score", "Grade"),
    rows=(
        ("Alice", "95", "A"),
        ("Bob",   "82", "B"),
    ),
)
```

When your data is naturally organized by column, use `Table.from_columns`.
Mapping order defines the rendered column order.

```python
Table.from_columns(
    {
        "Name": ("Alice", "Bob"),
        "Score": ("95", "82"),
        "Grade": ("A", "B"),
    },
)
```

Renders as:

```markdown
| Name | Score | Grade |
| --- | --- | --- |
| Alice | 95 | A |
| Bob | 82 | B |
```

Cell strings may be empty. A row with the wrong number of cells raises
`InvalidTableError`. `Table.from_columns` also raises `InvalidTableError`
when columns have different lengths. An empty `headers` tuple raises
`InvalidTableError`.

### BulletList and NumberedList

Unordered and ordered lists. Both require a **non-empty** tuple of
strings.

```python
BulletList(("apple", "banana", "cherry"))
# - apple
# - banana
# - cherry

NumberedList(("first step", "second step", "third step"))
# 1. first step
# 2. second step
# 3. third step
```

An empty tuple raises `ValueError`. A list passed instead of a tuple
raises `TypeError`.

### Image

A Markdown image reference. `path` is required and non-empty. `alt`
and `title` are optional.

```python
Image("chart.png")                               # ![](chart.png)
Image("chart.png", alt="Chart")                  # ![Chart](chart.png)
Image("chart.png", alt="Chart", title="Monthly") # ![Chart](chart.png "Monthly")
Image("https://example.com/img.png", alt="Logo") # remote URL
```

MkForge does **not** validate the path at construction time. Local path
existence is checked only when you call `report.save(...)`.

### HorizontalRule

A `---` separator. No arguments.

```python
HorizontalRule()
# ---
```

### BlockQuote

A Markdown block quote. Each line of `content` is prefixed with `> `.

```python
BlockQuote("Generated by automation.\nReviewed by humans.")
# > Generated by automation.
# > Reviewed by humans.
```

An empty string is accepted (renders as `> `). Non-string content
raises `TypeError`.

---

## Rendering

### Render to string

```python
markdown_text = report.render()
```

`render()` returns the full Markdown document as a `str`. It never
writes to disk. The call is deterministic and side-effect-free.

### Save to file

```python
report.save("output/report.md")
report.save("output/report.md", copy_assets=False)  # default
report.save("output/report.md", copy_assets=True)   # bundle images
```

`save()` does the following:

1. Collects every local image path in the tree.
2. Verifies that all local paths exist on disk → raises
   `MissingAssetError` if any are missing.
3. Renders the report to a string.
4. If `copy_assets=True`, copies local images into `assets/` next to
   the output file and rewrites image links; downloads remote images
   with SSRF protection.
5. Writes the UTF-8 Markdown file, creating parent directories as
   needed.

### Asset management

When `copy_assets=True`:

- **Local images** are copied to `<output_dir>/assets/<filename>`.
  Name collisions are resolved with a numeric suffix
  (`image.png`, `image_1.png`, …).
- **Remote images** (URLs starting with `://`, `//`, or `www.`) are
  downloaded. Only `http://`, `https://`, `ftp://`, and `ftps://`
  schemes are permitted. Loopback and private IP addresses are blocked
  (SSRF protection). Failed downloads raise `DownloadAssetError`.
- Image references in the rendered Markdown are rewritten to point
  inside `assets/`.

---

## Report Options

### YAML frontmatter

Pass a `dict` as `metadata` to prepend a YAML frontmatter block.
Keys must be non-empty strings. Values may be scalars, lists, or
`None`.

```python
Report(
    title="Audit",
    metadata={
        "title":   "Audit",
        "author":  "Alice",
        "date":    "2026-06-06",
        "version": "1.0.0",
        "tags":    ["quality", "audit"],
        "draft":   False,
        "reviewed": None,
    },
)
```

Renders as:

```yaml
---
title: Audit
author: Alice
date: 2026-06-06
version: 1.0.0
tags:
  - quality
  - audit
draft: false
reviewed: null
---
```

Supported value types:

| Python type | YAML rendering |
| --- | --- |
| `str` | verbatim string |
| `int` / `float` | `str(value)` |
| `bool` | `true` / `false` (lowercase) |
| `None` | `null` |
| `list` / `tuple` | YAML sequence with `  - ` items |

### Table of contents

Set `toc=True` to insert a nested Markdown list linking to every
chapter and section heading, positioned after the H1 title.

```python
Report(title="Report", toc=True).add(
    Chapter("Overview").add(
        Section("Background"),
        Section("Scope"),
    ),
    Chapter("Results"),
)
```

TOC fragment:

```markdown
- [Overview](#overview)
  - [Background](#background)
  - [Scope](#scope)
- [Results](#results)
```

Anchor slugs follow GitHub's rules: lowercase, spaces replaced with
hyphens, non-word characters removed.

### Automatic heading numbering

Set `auto_numbering=True` to prefix every heading with a dotted
counter.

```python
Report(title="Doc", auto_numbering=True).add(
    Chapter("Overview").add(
        Section("Background"),
        Section("Scope"),
    ),
    Chapter("Results"),
)
```

Headings produced:

```markdown
## 1. Overview
### 1.1. Background
### 1.2. Scope
## 2. Results
```

---

## Markdown Verification

MkForge includes a Markdown conformance checker that implements the
[markdownlint](https://github.com/DavidAnson/markdownlint) rule set
(MD001–MD047) plus GitHub Flavored Markdown rules (GFM001–GFM003)
and a local resource existence rule (MKF001).

### Verify a string

```python
from mkforge import verify_markdown

report = verify_markdown("# Title\n\nSome content.\n")

if report.passed:
    print("No issues found.")
else:
    for d in report.diagnostics:
        print(f"{d.rule_id} line {d.line}: {d.message}")
```

### Verify a file

```python
from mkforge import verify_markdown_file

report = verify_markdown_file("docs/README.md")
```

File verification also checks that local image and link targets exist
on disk (MKF001).

### VerificationReport

`VerificationReport` is a frozen dataclass with two fields:

| Field | Type | Description |
| --- | --- | --- |
| `rule_set_name` | `str` | Always `"markdown-compliance"` |
| `diagnostics` | `tuple[Diagnostic, ...]` | Sorted by `(line, column, rule_id)` |

The `passed` property returns `True` when `diagnostics` is empty.

### Diagnostic fields

| Field | Type | Example |
| --- | --- | --- |
| `rule_id` | `str` | `"MD018"` |
| `name` | `str` | `"no-missing-space-atx"` |
| `line` | `int` | `3` |
| `column` | `int` | `1` |
| `message` | `str` | `"No space after '#' in ATX heading"` |
| `category` | `str` | `"markdown-conformance"` |
| `severity` | `str` | `"warning"` |

### Disabling rules

Pass a `VerificationSettings` object with a `disabled` frozenset:

```python
from mkforge import VerificationSettings, verify_markdown

settings = VerificationSettings(disabled=frozenset({"MD013", "MD041"}))
report = verify_markdown(source, settings=settings)
```

Rule identifiers are case-insensitive in `disabled`.

### Custom rules

A custom rule is any callable with signature
`(MarkdownSource) -> tuple[Diagnostic, ...]`.

```python
from mkforge import (
    Diagnostic, MarkdownSource, MarkdownRule, verify_markdown,
)

def require_toc(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    if "## Table of Contents" not in source.text:
        return (
            Diagnostic(
                rule_id="ACME001",
                name="missing-toc",
                line=1,
                column=1,
                message="Document must include a Table of Contents section.",
            ),
        )
    return ()

report = verify_markdown(source_text, custom_rules=(require_toc,))
```

Custom rules are appended **after** all built-in rules. Their
diagnostics participate in the same sort and disable logic.

### TOML settings

Place a `.mkforge` or `.mkforge.toml` file next to your Markdown, or
add a `[tool.mkforge.verification]` table to `pyproject.toml`.
Settings are discovered automatically when you call
`verify_markdown_file`.

`.mkforge` example:

```toml
[verification]
disabled = ["MD013"]

[verification.rules.MD013]
line_length = 120
```

`pyproject.toml` example:

```toml
[tool.mkforge.verification]
disabled = ["MD034"]

[tool.mkforge.verification.rules.MD013]
line_length = 120
```

Supported settings keys:

| Key | Type | Description |
| --- | --- | --- |
| `disabled` | list of strings | Rule IDs to skip |
| `rules.<ID>.<option>` | any | Per-rule option overrides |

---

## Error Reference

| Exception | When raised | Key attributes |
| --- | --- | --- |
| `InvalidChildError` | Wrong child type added to a container | `.parent`, `.child` |
| `InvalidTableError` | Empty headers or row cell count mismatch | — |
| `ReportDepthError` | Section nesting exceeds H6 | — |
| `MissingAssetError` | Local image path does not exist at save time | `.missing` (tuple of `Path`) |
| `DownloadAssetError` | Remote image download fails | `.url`, `.reason` |

All exceptions inherit from `MkForgeError` → `Exception`.

---

## Complete Example

The following script generates a full CI quality report with
frontmatter, TOC, numbering, all content element types, and
Markdown verification of its own output.

```python
from pathlib import Path
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
    VerificationSettings,
    verify_markdown,
)

report = Report(
    title="CI Quality Report",
    metadata={
        "title":   "CI Quality Report",
        "author":  "CI Bot",
        "date":    "2026-06-06",
        "version": "1.0.0",
        "tags":    ["ci", "quality"],
        "draft":   False,
    },
    toc=True,
    auto_numbering=True,
).add(
    Chapter("Summary").add(
        Paragraph((
            Text("Build "),
            Text("passed", style="bold"),
            Text("."),
        )),
        Table(
            headers=("Check", "Status", "Duration"),
            rows=(
                ("lint",     "pass", "3 s"),
                ("tests",    "pass", "12 s"),
                ("coverage", "100 %", "—"),
            ),
        ),
    ),
    Chapter("Lint").add(
        Section("Tool").add(
            Paragraph((
                Text("Using "),
                Text("ruff", style="code"),
                Text(" v0.4.0."),
            )),
            BulletList(("E: errors", "W: warnings", "I: isort")),
        ),
        Section("Results").add(
            CodeBlock("ruff check src/\nAll checks passed.", language="sh"),
        ),
    ),
    Chapter("Tests").add(
        Section("Runner").add(
            NumberedList(("collect", "run", "report")),
        ),
        Section("Output").add(
            CodeBlock("pytest --tb=short\n5 passed in 0.12 s", language="sh"),
            BlockQuote("All tests passed.\nCoverage: 100 %."),
            HorizontalRule(),
            Paragraph((
                Text("Report generated by "),
                Link("https://github.com/example/mkforge", text="MkForge"),
                Text("."),
            )),
        ),
    ),
)

# Render to string and verify conformance
markdown = report.render()
settings = VerificationSettings(disabled=frozenset({"MD013"}))
result = verify_markdown(markdown, settings=settings)

if result.passed:
    print("Markdown is conformant.")
else:
    for d in result.diagnostics:
        print(f"  {d.rule_id} line {d.line}: {d.message}")

# Save to disk
output = Path("output/ci_quality_report.md")
report.save(output)
print(f"Saved to {output}")
```
