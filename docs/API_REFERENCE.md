# MkForge API Reference

## 1. Purpose

This reference documents every supported MkForge API surface, including public
classes, public exceptions, module-level helpers, complete examples, and UML
diagrams.

Runnable demonstrations: `demo_report.py` (report generation), `demo_verif.py`
(Markdown verification), and `demo_validation.py` (Markdown validation).

## 2. Import Model

Preferred user imports:

```python
from mkforge import (
    Chapter,
    Link,
    Paragraph,
    Report,
    Section,
    Table,
    slugify_heading,
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
    verify_markdown,
    verify_markdown_file,
)
```

Advanced helper imports:

```python
from mkforge.rendering import render_report, save_report, anchor_slug, NumberingContext
from mkforge.document import compute_section_heading_level
```

Verification-specific imports (all re-exported from `mkforge`):

```python
from mkforge import (
    Diagnostic,
    MarkdownLine,
    MarkdownRule,
    MarkdownSource,
    VerificationReport,
    VerificationSettings,
)
```

Validation-specific imports (all re-exported from `mkforge`):

```python
from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)
```

## 2.1 Public Surface Index

This table lists the supported public and advanced APIs documented in this
reference. Names exported by `mkforge` are the preferred application API.
Module-level helpers are documented for advanced integrations and tests.

| API | Import path | Category | Primary purpose |
|---|---|---|---|
| `Report` | `mkforge` | generation | Root Markdown document |
| `Chapter` | `mkforge` | generation | Top-level H2 report section |
| `Section` | `mkforge` | generation | Nested H3-H6 section |
| `Paragraph` | `mkforge` | content | Text block with optional inline elements |
| `Text` | `mkforge` | content | Styled inline text |
| `LineBreak` | `mkforge` | content | GFM hard line break |
| `Link` | `mkforge` | content | Inline Markdown link |
| `CodeBlock` | `mkforge` | content | Fenced code block |
| `Table` | `mkforge` | content | GFM pipe table |
| `BulletList` | `mkforge` | content | Unordered list |
| `NumberedList` | `mkforge` | content | Ordered list |
| `Image` | `mkforge` | content/assets | Markdown image reference |
| `HorizontalRule` | `mkforge` | content | Markdown thematic break |
| `BlockQuote` | `mkforge` | content | Markdown block quote |
| `verify_markdown` | `mkforge` | verification | Verify raw Markdown text |
| `verify_markdown_file` | `mkforge` | verification | Verify a Markdown file |
| `VerificationReport` | `mkforge` | verification | Verification result object |
| `Diagnostic` | `mkforge` | verification | One verification diagnostic |
| `MarkdownSource` | `mkforge` | verification | Rule execution context |
| `MarkdownLine` | `mkforge` | verification | One numbered source line |
| `MarkdownRule` | `mkforge` | verification | Custom rule callable protocol |
| `VerificationSettings` | `mkforge` | verification | Disabled rules and rule options |
| `validate_markdown_yaml` | `mkforge` | validation | Check YAML frontmatter contract |
| `validate_markdown_chapters` | `mkforge` | validation | Check H2 chapter contract |
| `validate_markdown_headings` | `mkforge` | validation | Check level/title heading contract |
| `validate_markdown_images` | `mkforge` | validation/assets | Check Markdown image targets |
| `slugify_heading` | `mkforge` | text | Convert a heading title to a GitHub-style anchor slug |
| `InvalidChildError` | `mkforge` | errors | Unsupported report-tree child |
| `InvalidTableError` | `mkforge` | errors | Invalid table shape |
| `ReportDepthError` | `mkforge` | errors | Section nesting below H6 |
| `MissingAssetError` | `mkforge` | errors/assets | Missing local image file |
| `DownloadAssetError` | `mkforge` | errors/assets | Remote asset download failure |
| `render_report` | `mkforge.rendering` | advanced | Render a `Report` object |
| `save_report` | `mkforge.rendering` | advanced | Render and write a report |
| `render_content_element` | `mkforge.rendering` | advanced | Render one content element |
| `anchor_slug` | `mkforge.rendering` | advanced | Compute GitHub-style anchor slug |
| `NumberingContext` | `mkforge.rendering` | advanced | Maintain heading counters |
| `compute_section_heading_level` | `mkforge.document` | advanced | Map section depth to heading level |
| `collect_local_image_paths` | `mkforge.assets` | advanced/assets | Collect local image paths from a report |
| `collect_remote_image_urls` | `mkforge.assets` | advanced/assets | Collect remote image URLs from a report |
| `verify_assets` | `mkforge.assets` | advanced/assets | Raise for missing local assets |
| `copy_assets_to_dir` | `mkforge.assets` | advanced/assets | Copy local images to an asset directory |
| `download_assets_to_dir` | `mkforge.assets` | advanced/assets | Download remote images to an asset directory |
| `rewrite_image_paths` | `mkforge.assets` | advanced/assets | Rewrite image references after bundling |

## 3. Complete Minimal Example

```python
from mkforge import Chapter, Paragraph, Report, Section

report = Report(
    title="Release Notes",
    metadata={"title": "Release Notes", "draft": False},
    toc=True,
    auto_numbering=True,
).add(
    Chapter("Summary").add(
        Section("Status").add(
            Paragraph("All checks passed."),
        ),
    ),
)

markdown = report.render()
report.save("work/release-notes.md")
```

Rendered heading hierarchy:

```markdown
# Release Notes

## 1. Summary

### 1.1. Status
```

---

## 4. Public Classes - Report Generation

### 4.1 `Report`

Module: `mkforge.document`

Exported by: `mkforge`

Signature:

```python
Report(
    title: str,
    children: list[Chapter] = ...,
    metadata: dict[str, object] | None = None,
    toc: bool = False,
    auto_numbering: bool = False,
)
```

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `title` | `str` | Document title rendered as the only H1 |
| `children` | `list[Chapter]` | Ordered chapters |
| `metadata` | `dict[str, object] | None` | Optional frontmatter dictionary |
| `toc` | `bool` | Whether to render a table of contents |
| `auto_numbering` | `bool` | Whether to number chapters and sections |

Methods:

| Method | Returns | Description |
|---|---|---|
| `add(*items: Chapter)` | `Report` | Appends chapters and returns self |
| `render()` | `str` | Renders full Markdown document |
| `save(path, *, copy_assets=False)` | `None` | Writes Markdown to a UTF-8 file; optionally copies images |

`save` parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str \| Path` | required | Destination file path |
| `copy_assets` | `bool` | `False` | When `True`, copies local and remote images into `assets/` next to the output file and rewrites image links |

Raises:

| Condition | Exception |
|---|---|
| Blank title | `ValueError` |
| Non-string title | `TypeError` |
| Non-dict metadata | `TypeError` |
| Non-string metadata key | `TypeError` |
| Non-bool `toc` or `auto_numbering` | `TypeError` |
| Invalid initial children collection | `TypeError` |
| Non-chapter passed to `add()` | `InvalidChildError` |
| Local image path does not exist | `MissingAssetError` |
| Remote image download fails (when `copy_assets=True`) | `DownloadAssetError` |

Example:

```python
from mkforge import Chapter, Report

report = Report(
    title="Quality Report",
    metadata={
        "title": "Quality Report",
        "author": "Antoine Barre",
        "tags": ["quality", "automation"],
        "draft": False,
        "reviewed": None,
    },
    toc=True,
    auto_numbering=True,
).add(
    Chapter("Overview"),
)
```

---

### 4.2 `Chapter`

Module: `mkforge.document`

Exported by: `mkforge`

Signature:

```python
Chapter(title: str, children: list[Section | ContentElement] = ...)
```

Rendering:

```markdown
## Chapter title
```

Methods:

| Method | Returns | Description |
|---|---|---|
| `add(*items)` | `Chapter` | Appends sections or content and returns self |

Raises:

| Condition | Exception |
|---|---|
| Blank title | `ValueError` |
| Non-string title | `TypeError` |
| Invalid initial children collection | `TypeError` |
| Unsupported child | `InvalidChildError` |

Example:

```python
from mkforge import Chapter, Paragraph

chapter = Chapter("Executive Summary").add(
    Paragraph("This report summarizes the release state."),
)
```

---

### 4.3 `Section`

Module: `mkforge.document`

Exported by: `mkforge`

Signature:

```python
Section(title: str, children: list[Section | ContentElement] = ...)
```

Rendering (depth-dependent):

```markdown
### Direct section
#### Nested section
##### Deeper section
###### Deepest supported section
```

Methods:

| Method | Returns | Description |
|---|---|---|
| `add(*items)` | `Section` | Appends nested sections or content and returns self |

Raises:

| Condition | Exception |
|---|---|
| Blank title | `ValueError` |
| Non-string title | `TypeError` |
| Invalid initial children collection | `TypeError` |
| Unsupported child | `InvalidChildError` |
| Section rendered below H6 | `ReportDepthError` |

Example:

```python
from mkforge import Paragraph, Section

section = Section("Risks").add(
    Section("Operational").add(
        Paragraph("No blocking operational risk was found."),
    ),
)
```

---

### 4.4 `Paragraph`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
Paragraph(content: str | tuple[Text | LineBreak | Link, ...])
```

Raises:

| Condition | Exception |
|---|---|
| `content == ""` for plain string content | `ValueError` |
| Non-string and non-tuple content | `TypeError` |
| Tuple item other than `Text`, `LineBreak`, or `Link` | `TypeError` |

Examples:

```python
from mkforge import Paragraph

plain = Paragraph("All checks passed.")
```

```python
from mkforge import LineBreak, Paragraph, Text

rich = Paragraph(
    (
        Text("MkForge renders "),
        Text("Markdown", style="bold"),
        Text(" from "),
        Text("Python", style="code"),
        Text("."),
        LineBreak(),
        Text("Inline styles remain explicit."),
    ),
)
```

---

### 4.5 `Text`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
Text(content: str, style: TextStyle = "plain")
```

Supported styles:

| Style | Output |
|---|---|
| `plain` | `text` |
| `bold` | `**text**` |
| `italic` | `*text*` |
| `code` | `` `text` `` |
| `strikethrough` | `~~text~~` |

Invalid runtime styles raise `ValueError`.

Example:

```python
from mkforge import Text

item = Text("auditable", style="bold")
```

---

### 4.6 `LineBreak`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
LineBreak()
```

Rendering:

```markdown
  
```

(Two trailing spaces followed by a newline - Markdown hard line break.)

Intended for use inside a `Paragraph` inline tuple.

---

### 4.7 `Link`

Module: `mkforge.content`

Exported by: `mkforge`

Inline element - valid only inside a `Paragraph` inline tuple.

Signature:

```python
Link(url: str, text: str = "", title: str = "")
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | required | Link target URL |
| `text` | `str` | `""` | Link display text; empty renders as `[]` |
| `title` | `str` | `""` | Optional tooltip title |

Rendering:

```markdown
[text](url)
[text](url "title")
```

Example:

```python
from mkforge import Link, Paragraph, Text

para = Paragraph(
    (
        Text("See the "),
        Link("https://example.com", text="documentation", title="Docs"),
        Text(" for details."),
    ),
)
```

---

### 4.8 `CodeBlock`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
CodeBlock(code: str, language: str = "")
```

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `code` | `str` | Raw fenced block body; may be empty |
| `language` | `str` | Optional info string after the opening fence |

Rendering rules:

| Input | Output |
|---|---|
| `CodeBlock("x = 1")` | Plain fenced code block |
| `CodeBlock("x = 1", language="python")` | Python fenced code block |
| `CodeBlock("", language="sh")` | Empty shell fenced code block |

Raises:

| Condition | Exception |
|---|---|
| Non-string `code` | `TypeError` |
| Non-string `language` | `TypeError` |

Example:

```python
from mkforge import CodeBlock

block = CodeBlock("print('hello from mkforge')", language="python")
```

Rendered output:

````markdown
```python
print('hello from mkforge')
```
````

---

### 4.9 `Table`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
Table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...] = ())
Table.from_columns(columns: Mapping[str, tuple[str, ...]])
```

Raises:

| Condition | Exception |
|---|---|
| No headers | `InvalidTableError` |
| Row width differs from header count | `InvalidTableError` |
| Column lengths differ in `from_columns` | `InvalidTableError` |
| Non-tuple headers or rows | `TypeError` |
| Non-mapping `from_columns` input | `TypeError` |
| Non-tuple column value | `TypeError` |
| Non-string header or cell | `TypeError` |

Example:

```python
from mkforge import Table

table = Table(
    headers=("Check", "Result"),
    rows=(
        ("format", "pass"),
        ("tests", "pass"),
    ),
)
```

Column-oriented construction:

```python
from mkforge import Table

table = Table.from_columns(
    {
        "Check": ("format", "tests"),
        "Result": ("pass", "pass"),
    },
)
```

---

### 4.10 `BulletList`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
BulletList(items: tuple[str, ...])
```

Raises:

| Condition | Exception |
|---|---|
| No items | `ValueError` |
| Non-tuple items | `TypeError` |
| Non-string item | `TypeError` |

Example:

```python
from mkforge import BulletList

scope = BulletList(("Markdown output", "Pure Python API"))
```

---

### 4.11 `NumberedList`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
NumberedList(items: tuple[str, ...])
```

Raises:

| Condition | Exception |
|---|---|
| No items | `ValueError` |
| Non-tuple items | `TypeError` |
| Non-string item | `TypeError` |

Example:

```python
from mkforge import NumberedList

steps = NumberedList(("Compose report", "Render Markdown", "Save file"))
```

---

### 4.12 `Image`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
Image(path: str, alt: str = "", title: str = "")
```

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `path` | `str` | Local path or remote image URL; may not be empty |
| `alt` | `str` | Alternate text; may be empty |
| `title` | `str` | Optional title text; may be empty |

Rendering rules:

| Input | Output |
|---|---|
| `Image("chart.png")` | `![](chart.png)` |
| `Image("chart.png", alt="Chart")` | `![Chart](chart.png)` |
| `Image("chart.png", alt="Chart", title="Q1")` | `![Chart](chart.png "Q1")` |

Validation and asset behavior:

- construction does not check local filesystem existence;
- `Report.save()` checks all local image paths before writing;
- `Report.save(copy_assets=True)` copies local images into `assets/`;
- remote image URLs are downloaded only when `copy_assets=True`;
- remote download failures raise `DownloadAssetError`.

Raises:

| Condition | Exception |
|---|---|
| Empty `path` | `ValueError` |
| Non-string `path`, `alt`, or `title` | `TypeError` |

Example:

```python
from mkforge import Image

image = Image(
    "assets/quality-dashboard.png",
    alt="Quality dashboard",
    title="Release quality",
)
```

Rendered output:

```markdown
![Quality dashboard](assets/quality-dashboard.png "Release quality")
```

---

### 4.13 `HorizontalRule`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
HorizontalRule()
```

Rendered output:

```markdown
---
```

---

### 4.14 `BlockQuote`

Module: `mkforge.content`

Exported by: `mkforge`

Signature:

```python
BlockQuote(content: str)
```

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `content` | `str` | Quote body; may contain multiple lines |

Rendering rules:

- each line is prefixed with `> `;
- embedded newlines are preserved as quoted lines;
- an empty string renders as `> `;
- non-string content raises `TypeError`.

Example:

```python
from mkforge import BlockQuote

quote = BlockQuote("Readable reports are easier to review.")
```

Rendered output:

```markdown
> Readable reports are easier to review.
```

---

## 5. Public Exceptions

### 5.1 `InvalidChildError`

Raised when an unsupported object is added to `Report`, `Chapter`, or
`Section`.

String form:

```text
Report cannot contain Paragraph.
```

### 5.2 `InvalidTableError`

Raised when a `Table` cannot be rendered as a valid GFM table.

### 5.3 `ReportDepthError`

Raised when a nested section would render below H6.

### 5.4 `MissingAssetError`

Raised by `save()` / `save_report()` when one or more local image paths do
not exist on disk before writing the output file.

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `missing` | `tuple[Path, ...]` | All missing paths, in the order they were found |

String form:

```text
Missing asset files: /project/chart.png, /project/logo.png
```

### 5.5 `DownloadAssetError`

Raised by `save(copy_assets=True)` / `save_report(copy_assets=True)` when a
remote image URL cannot be downloaded.

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `url` | `str` | The URL that failed |
| `reason` | `str` | The failure reason |

Raised for:
- Unsupported URL schemes (only `http`, `https`, `ftp`, `ftps` are allowed)
- Hostnames that resolve to private or loopback addresses (SSRF protection)
- Network errors (`URLError`)

String form:

```text
Failed to download asset 'https://example.com/img.png': <urlopen error timeout>
```

---

## 6. Module-Level Functions - Report Generation

### 6.1 `mkforge.rendering.render_report`

Signature:

```python
render_report(report: Report) -> str
```

Renders a full Markdown document. Equivalent to `report.render()`.

### 6.2 `mkforge.rendering.save_report`

Signature:

```python
save_report(report: Report, path: str | Path, *, copy_assets: bool = False) -> None
```

Writes a full Markdown document to a UTF-8 file. Equivalent to
`report.save(path, copy_assets=copy_assets)`.

When `copy_assets=True`:

1. Local image files are copied into an `assets/` directory next to `path`.
2. Remote image URLs are downloaded into the same `assets/` directory.
3. All image links in the rendered Markdown are rewritten to `assets/<filename>`.

Filename collisions (two images sharing a basename) are renamed with a `_N`
suffix and a `UserWarning` is emitted.

Raises `MissingAssetError` if any local image is absent.  Raises
`DownloadAssetError` if a remote download fails.

### 6.3 `mkforge.rendering.anchor_slug`

Signature:

```python
anchor_slug(title: str) -> str
```

Converts a heading title to a GitHub-style anchor slug.

Example:

```python
anchor_slug("Hello, 2026!") == "hello-2026"
```

### 6.4 `mkforge.rendering.NumberingContext`

Tracks heading counters during rendering traversal.

Methods:

| Method | Description |
|---|---|
| `enter_level()` | Pushes a new zero counter |
| `leave_level()` | Pops the active counter |
| `advance()` | Increments the active counter |
| `prefix()` | Returns the dotted prefix string (e.g. `1.2.`) |

### 6.5 `mkforge.document.compute_section_heading_level`

Signature:

```python
compute_section_heading_level(depth_from_chapter: int) -> int
```

Returns the Markdown heading level (3-6) for a section at a given nesting
depth below its parent chapter. Raises `ReportDepthError` when the level
would exceed H6.

---

## 6.6 `mkforge.assets` Helpers

These helpers are used internally by `save_report`, but they are documented for
advanced integrations that need to inspect or bundle assets explicitly.

### 6.6.1 `collect_local_image_paths`

Signature:

```python
collect_local_image_paths(report: object) -> list[Path]
```

Walks a `Report` tree and returns resolved filesystem paths for every local
`Image`. Remote images are excluded. Duplicates are preserved in document
order.

| Input | Result |
|---|---|
| non-`Report` object | `[]` |
| report with no images | `[]` |
| report with `Image("chart.png")` | `[Path("chart.png").resolve()]` |

### 6.6.2 `collect_remote_image_urls`

Signature:

```python
collect_remote_image_urls(report: object) -> list[str]
```

Walks a `Report` tree and returns remote image references in document order.
Local images are excluded. A path is treated as remote when it contains
`://`, starts with `//`, or starts with `www.`.

### 6.6.3 `verify_assets`

Signature:

```python
verify_assets(paths: list[Path]) -> None
```

Checks that every given path exists. Missing paths are collected and raised in
one `MissingAssetError`.

Raises:

| Condition | Exception |
|---|---|
| Any path does not exist | `MissingAssetError` |

### 6.6.4 `copy_assets_to_dir`

Signature:

```python
copy_assets_to_dir(paths: list[Path], assets_dir: Path) -> dict[Path, str]
```

Copies local image files into `assets_dir` and returns a mapping from original
resolved path to rewritten Markdown path.

Behavior:

- creates `assets_dir` when needed;
- skips duplicate source paths;
- preserves metadata via `shutil.copy2`;
- resolves basename collisions by appending `_N`;
- emits `UserWarning` for collision renames;
- returns values such as `assets/chart.png`.

Example return value:

```python
{
    Path("/project/chart.png"): "assets/chart.png",
    Path("/project/other/chart.png"): "assets/chart_1.png",
}
```

### 6.6.5 `download_assets_to_dir`

Signature:

```python
download_assets_to_dir(urls: list[str], assets_dir: Path) -> dict[str, str]
```

Downloads remote image URLs into `assets_dir` and returns a mapping from URL to
rewritten Markdown path.

Behavior:

- creates `assets_dir` when needed;
- skips duplicate URLs;
- derives filenames from the URL path;
- uses `image_<n>` when the URL has no usable filename;
- resolves filename collisions by appending `_N`;
- emits `UserWarning` for collision renames;
- permits only `http`, `https`, `ftp`, and `ftps` schemes;
- blocks hosts that resolve to private, loopback, link-local, unspecified, or
  multicast addresses.

Raises:

| Condition | Exception |
|---|---|
| Unsupported scheme | `DownloadAssetError` |
| URL has no host | `DownloadAssetError` |
| Host resolves to non-routable address | `DownloadAssetError` |
| Network download fails | `DownloadAssetError` |

### 6.6.6 `rewrite_image_paths`

Signature:

```python
rewrite_image_paths(
    markdown: str,
    local_map: dict[Path, str],
    remote_map: dict[str, str] | None = None,
) -> str
```

Rewrites Markdown image references after local copying or remote download.

Behavior:

- replaces resolved local paths with their `assets/<filename>` path;
- also replaces local basenames for simple relative image references;
- replaces remote URLs with their downloaded `assets/<filename>` path;
- treats `remote_map=None` as an empty mapping;
- returns a new Markdown string.

---

## 6.7 `mkforge.slugify` Helpers

### 6.7.1 `slugify_heading`

Module: `mkforge.slugify`

Exported by: `mkforge`

Signature:

```python
slugify_heading(text: str) -> str
```

Converts a raw Markdown heading title (without leading `#` markers) into a
GitHub-compatible anchor slug. This is the same slug shape GitHub computes for
heading anchors, so it can be used to build stable cross-document links, for
example from `scribpy` when it assembles Markdown collections authored with
MkForge.

Algorithm:

1. Strip inline Markdown markers: `` ` ``, `*`, `_`, `~`.
2. Lowercase the text (Unicode letters are case-folded, never
   transliterated).
3. Collapse every run of characters that is neither alphanumeric nor a
   literal hyphen into a single `-`.
4. Trim leading and trailing hyphens.

Parameters:

| Parameter | Type | Description |
|---|---|---|
| `text` | `str` | Raw heading text, without the leading `#` markers |

Returns: `str` — lowercase, hyphen-separated anchor slug.

Raises:

| Condition | Exception |
|---|---|
| `text` is not a string | `TypeError` |

Examples:

```python
from mkforge import slugify_heading

slugify_heading("Hello World")          # "hello-world"
slugify_heading("Analyse des Risques")  # "analyse-des-risques"
slugify_heading("C'est l'été !")        # "c-est-l-été"
slugify_heading("`code` inline")        # "code-inline"
slugify_heading("  leading spaces  ")   # "leading-spaces"
slugify_heading("A & B")                # "a-b"
```

Note: `mkforge.rendering.anchor_slug` (advanced, internal) powers MkForge's
own table-of-contents generation and is not identical to `slugify_heading` on
every input (for example, it drops apostrophes instead of turning them into a
separator). Use `slugify_heading` for anchors shared with external tools;
`anchor_slug` remains reserved for MkForge's internal TOC rendering.

---

## 7. Metadata Reference

Metadata is a free-form dictionary. MkForge does not define allowed keys.

Example:

```python
metadata = {
    "title": "Audit",
    "author": "Antoine Barre",
    "tags": ["quality", "markdown"],
    "draft": False,
    "reviewed": None,
}
```

Rendered output:

```markdown
---
title: Audit
author: Antoine Barre
tags:
  - quality
  - markdown
draft: false
reviewed: null
---
```

Value rendering rules:

| Python type | Frontmatter output |
|---|---|
| `list` / `tuple` | YAML block list (`- item`) |
| `bool` | `true` or `false` (lowercase) |
| `None` | `null` |
| anything else | `str(value)` |

---

## 8. Verification API

MkForge exposes a focused API for Markdown and GitHub Flavored Markdown
conformance verification. The built-in policy is merged: one call checks
classic Markdown syntax, GFM tables, GFM task list markers, and MkForge local
resource references when a file path is available.

### 8.1 `verify_markdown`

Module: `mkforge.verification.api`

Exported by: `mkforge`

Signature:

```python
verify_markdown(
    source: str,
    *,
    source_path: str | Path | None = None,
    settings: VerificationSettings | None = None,
    custom_rules: Iterable[MarkdownRule] = (),
) -> VerificationReport
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `source` | `str` | required | Markdown source text |
| `source_path` | `str | Path | None` | `None` | Path used for resource resolution and settings discovery |
| `settings` | `VerificationSettings | None` | `None` | In-memory settings; when absent, settings are discovered from TOML files near `source_path` |
| `custom_rules` | `Iterable[MarkdownRule]` | `()` | Additional rule callables appended after built-in rules |

Returns: `VerificationReport`

Raises: nothing (rule errors are not suppressed; malformed rules may raise
internally).

Example:

```python
from mkforge import verify_markdown

report = verify_markdown("# Title\n\n| A | B |\n| --- | --- |\n")
print(report.passed)       # True
print(report.rule_set_name)  # "markdown-compliance"
```

---

### 8.2 `verify_markdown_file`

Module: `mkforge.verification.api`

Exported by: `mkforge`

Signature:

```python
verify_markdown_file(
    path: str | Path,
    *,
    settings: VerificationSettings | None = None,
    custom_rules: Iterable[MarkdownRule] = (),
) -> VerificationReport
```

Reads the file as UTF-8 and delegates to `verify_markdown`. The file path is
used automatically as `source_path` for resource resolution and settings
discovery.

Raises: `FileNotFoundError` when `path` does not exist.

Example:

```python
from mkforge import verify_markdown_file

report = verify_markdown_file("docs/README.md")
for d in report.diagnostics:
    print(f"[{d.rule_id}] line {d.line}: {d.message}")
```

---

### 8.3 `VerificationReport`

Module: `mkforge.verification.api`

Exported by: `mkforge`

Frozen dataclass.

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `rule_set_name` | `str` | Name of the built-in rule set (`"markdown-compliance"`) |
| `diagnostics` | `tuple[Diagnostic, ...]` | Sorted diagnostics, ordered by `(line, column, rule_id)` |
| `passed` | `bool` | `True` when `diagnostics` is empty |

---

### 8.4 `Diagnostic`

Module: `mkforge.verification.policy`

Exported by: `mkforge`

Frozen dataclass.

Attributes:

| Attribute | Type | Default | Description |
|---|---|---|---|
| `rule_id` | `str` | required | Stable rule identifier |
| `name` | `str` | required | Human-readable rule name |
| `line` | `int` | required | One-based source line |
| `column` | `int` | required | One-based source column |
| `message` | `str` | required | Precise diagnostic message |
| `category` | `str` | `"markdown-conformance"` | Diagnostic category |
| `severity` | `str` | `"warning"` | Diagnostic severity |

Custom rule example:

```python
from mkforge import Diagnostic, MarkdownSource

def check_marker(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Report the custom BAD_MARKER token."""
    return tuple(
        Diagnostic(
            rule_id="X001",
            name="Custom marker",
            line=line.number,
            column=line.text.index("BAD_MARKER") + 1,
            message="Remove BAD_MARKER.",
        )
        for line in source.lines
        if "BAD_MARKER" in line.text
    )
```

---

### 8.5 `MarkdownSource`

Module: `mkforge.verification.policy`

Exported by: `mkforge`

Frozen dataclass. Passed as the sole argument to every rule callable.

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `text` | `str` | Full Markdown source text |
| `lines` | `tuple[MarkdownLine, ...]` | Pre-split one-based source lines |
| `path` | `Path | None` | Source path; `None` when verifying raw text |
| `settings` | `VerificationSettings` | Active verification settings |

Class method:

```python
MarkdownSource.from_text(
    text: str,
    *,
    source_path: str | Path | None = None,
    settings: VerificationSettings | None = None,
) -> MarkdownSource
```

Instance method:

```python
source.rule_options(rule_id: str) -> dict[str, object]
```

Returns the configured option mapping for a given rule identifier.

---

### 8.6 `MarkdownLine`

Module: `mkforge.verification.policy`

Exported by: `mkforge`

Frozen dataclass.

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `number` | `int` | One-based line number |
| `text` | `str` | Raw line text without trailing newline |

---

### 8.7 `MarkdownRule`

Module: `mkforge.verification.policy`

Exported by: `mkforge`

Type alias:

```python
type MarkdownRule = Callable[[MarkdownSource], tuple[Diagnostic, ...]]
```

Any callable with this signature is a valid rule. Built-in rules and custom
rules are structurally identical.

---

### 8.8 `VerificationSettings`

Module: `mkforge.verification.settings`

Exported by: `mkforge`

Frozen dataclass.

Signature:

```python
VerificationSettings(
    disabled: frozenset[str] = frozenset(),
    rules: dict[str, RuleOptions] = ...,
)
```

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `disabled` | `frozenset[str]` | Rule identifiers to skip |
| `rules` | `dict[str, RuleOptions]` | Per-rule option mappings |

Method:

```python
settings.rule_options(rule_id: str) -> dict[str, object]
```

Examples:

```python
from mkforge import VerificationSettings, verify_markdown

# Disable a rule
report = verify_markdown(
    "# Title\n\n![img](missing.png)\n",
    settings=VerificationSettings(disabled=frozenset({"MKF001"})),
)
```

```python
# Override rule options
report = verify_markdown(
    "# Title\n\nThis line is quite long.\n",
    settings=VerificationSettings(
        rules={"MD013": {"line_length": 40}},
    ),
)
```

---

## 8.9 Validation API

Module: `mkforge.validation`

Exported by: `mkforge`

Validation functions return booleans for project-specific document contracts.
They do not emit Markdown/GFM compliance diagnostics. Use verification when
you need line-numbered Markdown diagnostics; use validation when you need a
yes/no answer for expected content.

### 8.9.1 `validate_markdown_yaml`

Signature:

```python
validate_markdown_yaml(
    markdown: str,
    expected: Mapping[str, object],
    *,
    strict: bool = False,
) -> bool
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `markdown` | `str` | required | Markdown source text |
| `expected` | `Mapping[str, object]` | required | Expected frontmatter keys and values |
| `strict` | `bool` | `False` | Whether the key set must match exactly |

Return value:

| Result | Meaning |
|---|---|
| `True` | Frontmatter exists and matches the expected contract |
| `False` | Frontmatter is missing, malformed, or does not match |

Contract rules:

- frontmatter must appear at the start of the document;
- frontmatter must be delimited by `---` lines;
- non-strict mode treats `expected` as a minimum mapping;
- strict mode requires exactly the expected keys;
- concrete expected values compare by value;
- expected Python types such as `bool`, `int`, or `str` compare by type only;
- list expectations compare list length and item contracts.

Supported parsed values:

| YAML source | Parsed value |
|---|---|
| `draft: false` | `False` |
| `count: 3` | `3` |
| `ratio: 1.5` | `1.5` |
| `reviewed: null` | `None` |
| `tags:` followed by `  - item` lines | `list[object]` |

Raises:

| Condition | Exception |
|---|---|
| `markdown` is not a string | `TypeError` |
| `expected` is not a mapping | `TypeError` |

Example:

```python
from mkforge import validate_markdown_yaml

markdown = """---
title: Release
draft: false
version: 3
tags:
  - release
  - docs
---

# Release
"""

validate_markdown_yaml(markdown, {"draft": False})
validate_markdown_yaml(markdown, {"version": int})
validate_markdown_yaml(
    markdown,
    {
        "title": "Release",
        "draft": False,
        "version": 3,
        "tags": ["release", "docs"],
    },
    strict=True,
)
```

### 8.9.2 `validate_markdown_chapters`

Signature:

```python
validate_markdown_chapters(
    markdown: str,
    expected: Iterable[str],
    *,
    strict: bool = False,
) -> bool
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `markdown` | `str` | required | Markdown source text |
| `expected` | `Iterable[str]` | required | Expected H2 chapter titles |
| `strict` | `bool` | `False` | Whether the full H2 sequence must match |

Return value:

| Result | Meaning |
|---|---|
| `True` | Expected chapters match according to the selected mode |
| `False` | H2 chapters are missing, out of order, or not exact in strict mode |

Contract rules:

- only H2 headings (`## Title`) are considered chapters;
- H1, H3, H4, H5, and H6 headings are ignored;
- non-strict mode checks ordered subsequence membership;
- strict mode checks complete H2 equality;
- title comparison is exact after Markdown heading marker parsing.

Raises:

| Condition | Exception |
|---|---|
| `markdown` is not a string | `TypeError` |
| `expected` is not a valid string sequence | `TypeError` |

Example:

```python
from mkforge import validate_markdown_chapters

markdown = """# Report

## Context

## Architecture

## Tests
"""

validate_markdown_chapters(markdown, ("Context", "Tests"))
validate_markdown_chapters(
    markdown,
    ("Context", "Architecture", "Tests"),
    strict=True,
)
```

### 8.9.3 `validate_markdown_headings`

Signature:

```python
validate_markdown_headings(
    markdown: str,
    expected: Iterable[tuple[int, str]],
    *,
    strict: bool = False,
) -> bool
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `markdown` | `str` | required | Markdown source text |
| `expected` | `Iterable[tuple[int, str]]` | required | Expected `(level, title)` contracts |
| `strict` | `bool` | `False` | Whether the full heading sequence must match |

Return value:

| Result | Meaning |
|---|---|
| `True` | Heading level/title pairs match according to selected mode |
| `False` | A heading is missing, at the wrong level, or out of order |

Contract rules:

- headings are represented as `(level, title)`;
- `level` must be an integer from 1 to 6;
- `title` must be a non-empty string;
- non-strict mode checks ordered subsequence membership;
- strict mode checks the complete heading sequence;
- use this function when heading level is part of the contract.

Raises:

| Condition | Exception |
|---|---|
| `markdown` is not a string | `TypeError` |
| `expected` is not an iterable of pairs | `TypeError` |
| heading level is not an integer | `TypeError` |
| heading level is outside 1-6 | `ValueError` |
| heading title is blank | `ValueError` |

Example:

```python
from mkforge import validate_markdown_headings

markdown = """# Report

## Context

### Scope

## Tests
"""

validate_markdown_headings(
    markdown,
    ((2, "Context"), (3, "Scope"), (2, "Tests")),
)
```

### 8.9.4 `validate_markdown_images`

Signature:

```python
validate_markdown_images(
    markdown: str,
    *,
    base_path: str | Path | None = None,
    timeout: float = 5.0,
) -> bool
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `markdown` | `str` | required | Markdown source text |
| `base_path` | `str | Path | None` | `None` | Directory or Markdown file used for local path resolution |
| `timeout` | `float` | `5.0` | Timeout in seconds for remote HTTP checks |

Return value:

| Result | Meaning |
|---|---|
| `True` | Every image target outside fenced code blocks exists or is reachable |
| `False` | At least one image target is empty, missing, blocked, or unreachable |

Contract rules:

- fenced code blocks are ignored;
- local paths resolve from `base_path`;
- if `base_path` points to a file, local paths resolve from its parent;
- if `base_path` is omitted, local paths resolve from the current directory;
- remote image checks support HTTP and HTTPS;
- remote checks try `HEAD`, then `GET` as a fallback;
- loopback and private hosts are rejected before network access.

Raises:

| Condition | Exception |
|---|---|
| `markdown` is not a string | `TypeError` |
| `base_path` is an empty string | `ValueError` |
| `timeout` is not a number | `TypeError` |
| `timeout` is less than or equal to zero | `ValueError` |

Example:

```python
from mkforge import validate_markdown_images

markdown = "# Report\n\n![Chart](assets/chart.png)\n"

validate_markdown_images(markdown, base_path="docs/report.md")
```

### 8.9.5 Combined validation gate

```python
from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)

ok = (
    validate_markdown_yaml(markdown, {"draft": False})
    and validate_markdown_chapters(markdown, ("Context", "Tests"))
    and validate_markdown_headings(markdown, ((2, "Context"), (3, "Scope")))
    and validate_markdown_images(markdown, base_path="doc/release.md")
)
```

---

## 9. Built-in Rule Reference

### 9.1 Rule Identifier Prefixes

| Prefix | Scope |
|---|---|
| `MD001`-`MD047` | markdownlint-compatible Markdown conformance checks |
| `GFM001`-`GFM003` | GitHub Flavored Markdown verification |
| `MKF001` | MkForge resource verification |

### 9.2 Markdown Rules (MD prefix)

| Rule ID | Name | Description |
|---|---|---|
| `MD001` | Heading increment | Heading levels must increment by one at a time |
| `MD002` | First heading level | First heading must be the configured level |
| `MD003` | Heading style | All headings must use a consistent style |
| `MD004` | Unordered list style | Unordered list markers must be consistent |
| `MD005` | List indentation consistency | List indentation must be consistent |
| `MD006` | Top-level list indentation | Top-level unordered lists must not be indented |
| `MD007` | Unordered list indentation | Unordered list indentation must match configured value |
| `MD009` | Trailing spaces | Lines must not have unnecessary trailing spaces |
| `MD010` | Hard tabs | Lines must not contain hard tab characters |
| `MD011` | Reversed link syntax | Links must use `[text](url)` not `(text)[url]` |
| `MD012` | Multiple blank lines | No more than one consecutive blank line |
| `MD013` | Line length | Lines must not exceed the configured length |
| `MD014` | Command prompt | Shell prompt markers unnecessary in command-only blocks |
| `MD018` | ATX heading spacing | ATX headings require a space after `#` |
| `MD019` | ATX heading extra spaces | ATX headings must not have multiple spaces after `#` |
| `MD020` | Closed ATX spacing | Closed ATX headings require a space before closing `#` |
| `MD021` | Closed ATX extra spaces | Closed ATX headings must not have multiple spaces inside |
| `MD022` | Heading blank lines | Headings must be surrounded by blank lines |
| `MD023` | Heading alignment | Headings must start at the beginning of the line |
| `MD024` | Duplicate headings | Headings must not have duplicate content |
| `MD025` | Multiple top-level headings | Only one H1 heading allowed |
| `MD026` | Heading punctuation | Headings must not end with punctuation |
| `MD027` | Blockquote spacing | Blockquote markers must have one space after `>` |
| `MD028` | Blank blockquote line | No blank lines inside a blockquote |
| `MD029` | Ordered list prefix | Ordered list items must use the configured prefix style |
| `MD030` | List marker spacing | Spaces after list markers must match configured value |
| `MD031` | Fence blank lines | Fenced code blocks must be surrounded by blank lines |
| `MD032` | List blank lines | Lists must be surrounded by blank lines |
| `MD033` | Inline HTML | Inline HTML is not allowed (except configured elements) |
| `MD034` | Bare URL | URLs must not appear bare; wrap in `<url>` or `[text](url)` |
| `MD035` | Horizontal rule style | Horizontal rules must use a consistent style |
| `MD036` | Emphasis as heading | Emphasis must not be used as a heading substitute |
| `MD037` | Emphasis marker spacing | No spaces inside emphasis markers |
| `MD038` | Code span spacing | No spaces inside code span markers |
| `MD039` | Link text spacing | No spaces inside link text brackets |
| `MD040` | Fence language | Fenced code blocks must specify a language |
| `MD041` | First line heading | First line must be a heading |
| `MD046` | Code block style | Code blocks must use the configured style |
| `MD047` | Single trailing newline | Files must end with exactly one newline |

### 9.3 GFM Rules (GFM prefix)

| Rule ID | Name | Description |
|---|---|---|
| `GFM001` | GFM table delimiter | Each delimiter cell must have at least three hyphens |
| `GFM002` | GFM table column count | Table rows must have the same column count as the header |
| `GFM003` | GFM task list marker | Task list markers must be `[ ]` or `[x]` |

### 9.4 MkForge Rules (MKF prefix)

| Rule ID | Name | Description |
|---|---|---|
| `MKF001` | Local resource exists | Relative link and image targets must resolve from the source file directory |

`MKF001` is only active when `source_path` is provided. Fragment-only links
(`#anchor`) and remote URLs are not checked.

### 9.5 Configurable Rule Options

| Rule ID | Option | Default | Description |
|---|---|---|---|
| `MD002` | `level` | `1` | Expected first heading level |
| `MD003` | `style` | `"consistent"` | `atx`, `atx_closed`, `setext`, `setext_with_atx`, `consistent` |
| `MD004` | `style` | `"consistent"` | `asterisk`, `plus`, `dash`, `consistent` |
| `MD007` | `indent` | `3` | Spaces per unordered list indent level |
| `MD009` | `br_spaces` | `2` | Trailing spaces allowed for hard line break |
| `MD010` | `ignore_code_blocks` | `False` | Skip hard tab check inside fenced code |
| `MD013` | `line_length` | `80` | Maximum line character count |
| `MD013` | `ignore_code_blocks` | `False` | Skip line length inside fenced code |
| `MD013` | `tables` | `True` | Enforce line length in tables |
| `MD013` | `headings` | `True` | Enforce line length in headings |
| `MD024` | `allow_different_nesting` | `False` | Allow same text at different heading levels |
| `MD025` | `level` | `1` | Heading level considered top-level |
| `MD026` | `punctuation` | `".,;:!?"` | Characters that must not end a heading |
| `MD029` | `style` | `"one"` | `one`, `ordered`, `zero` |
| `MD030` | `ul_single` | `1` | Spaces after unordered marker, single-line item |
| `MD030` | `ol_single` | `1` | Spaces after ordered marker, single-line item |
| `MD030` | `ul_multi` | `1` | Spaces after unordered marker, multi-line item |
| `MD030` | `ol_multi` | `1` | Spaces after ordered marker, multi-line item |
| `MD033` | `allowed_elements` | `""` | Comma-separated HTML element names that are permitted |
| `MD035` | `style` | `"consistent"` | `---`, `***`, `___`, `consistent` |
| `MD036` | `punctuation` | `".,;:!?"` | Trailing characters that identify emphasis-as-heading |
| `MD041` | `level` | `1` | Required level of the first-line heading |
| `MD046` | `style` | `"fenced"` | `fenced`, `indented`, `consistent` |

---

## 10. Settings Configuration

Settings are discovered automatically when `source_path` is provided. MkForge
searches from the source file directory upward for the first directory
containing any of:

1. `pyproject.toml` - read from `[tool.mkforge.verification]`
2. `.mkforge.toml` - read from `[verification]` or root table
3. `.mkforge` - read from `[verification]` or root table

Example `pyproject.toml`:

```toml
[tool.mkforge.verification]
disabled = ["MD013", "MD033"]

[tool.mkforge.verification.rules.MD003]
style = "atx"

[tool.mkforge.verification.rules.MD013]
line_length = 100
headings = false
```

Example `.mkforge.toml`:

```toml
[verification]
disabled = ["MD002"]

[verification.rules.MD004]
style = "dash"
```

Merge semantics: per-rule options are merged key-by-key over defaults; the
`disabled` set is unioned.

---

## 11. Custom Rules

A custom rule is any callable with the `MarkdownRule` signature:

```python
type MarkdownRule = Callable[[MarkdownSource], tuple[Diagnostic, ...]]
```

Custom rules are appended after built-in rules and run in the order given.
They receive the same `MarkdownSource` context and may use `source.lines`,
`source.text`, `source.path`, and `source.rule_options()`.

Full custom rule example:

```python
from mkforge import (
    Diagnostic,
    MarkdownRule,
    MarkdownSource,
    verify_markdown,
)


def check_todo(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for unresolved TODO markers."""
    return tuple(
        Diagnostic(
            rule_id="TEAM001",
            name="Unresolved TODO",
            line=line.number,
            column=line.text.index("TODO:") + 1,
            message="Resolve or remove this TODO before publishing.",
        )
        for line in source.lines
        if "TODO:" in line.text
    )


rules: tuple[MarkdownRule, ...] = (check_todo,)

report = verify_markdown(
    "# Title\n\nTODO: finish this section\n",
    custom_rules=rules,
)
```

---

## 12. Feature Reference

This section documents cross-cutting features whose behavior spans multiple
classes or functions.

### 12.1 Fluent Report Construction

Feature owner: `Report.add`, `Chapter.add`, `Section.add`

Behavior:

- `Report.add(*chapters)` appends one or more chapters and returns the same
  `Report` instance;
- `Chapter.add(*items)` appends sections or content elements and returns the
  same `Chapter` instance;
- `Section.add(*items)` appends nested sections or content elements and
  returns the same `Section` instance;
- invalid child types fail immediately with `InvalidChildError`.

Example:

```python
report = Report("Quality").add(
    Chapter("Summary").add(
        Paragraph("All checks passed."),
    ),
)
```

### 12.2 Heading Model

Feature owners: `Report`, `Chapter`, `Section`,
`compute_section_heading_level`

Rendering contract:

| Object | Heading level |
|---|---|
| `Report` | H1 |
| `Chapter` | H2 |
| `Section` directly under chapter | H3 |
| nested section depth 2 | H4 |
| nested section depth 3 | H5 |
| nested section depth 4 | H6 |

Errors:

- section depth below H6 raises `ReportDepthError`;
- invalid depth passed to `compute_section_heading_level` raises `TypeError`
  or `ValueError`.

### 12.3 Frontmatter Rendering

Feature owners: `Report.metadata`, `render_report`

Behavior:

- frontmatter is rendered only when `Report.metadata is not None`;
- metadata keys must be non-empty strings;
- dictionary insertion order is preserved;
- output is enclosed by `---` delimiters;
- list and tuple values render as YAML block sequences.

Example:

```python
Report(
    "Audit",
    metadata={"title": "Audit", "draft": False, "tags": ["ci", "release"]},
)
```

Rendered:

```markdown
---
title: Audit
draft: false
tags:
  - ci
  - release
---
```

### 12.4 Table Of Contents

Feature owners: `Report.toc`, `anchor_slug`

Behavior:

- TOC renders after H1 and before chapters;
- chapters and sections are included;
- empty reports do not render an empty TOC block;
- anchors use `anchor_slug(title)`;
- anchors are based on raw titles, not numbered titles.

Example:

```python
Report("Doc", toc=True).add(
    Chapter("Intro").add(
        Section("Scope"),
    ),
)
```

TOC:

```markdown
- [Intro](#intro)
  - [Scope](#scope)
```

### 12.5 Automatic Heading Numbering

Feature owners: `Report.auto_numbering`, `NumberingContext`

Behavior:

- chapters receive `1.`, `2.`, `3.` prefixes;
- sections receive nested prefixes such as `1.1.` and `1.2.`;
- numbering affects rendered headings;
- numbering does not mutate stored `title` attributes;
- numbering and TOC can be enabled together.

Example output:

```markdown
## 1. Summary

### 1.1. Status

## 2. Evidence
```

### 12.6 Content Rendering

Feature owners: content element `.render()` methods,
`render_content_element`

Behavior:

- each content element owns its Markdown rendering;
- `render_content_element` accepts objects satisfying the `Renderable`
  protocol;
- unknown content raises `TypeError`;
- report traversal joins blocks with one blank line between blocks.

### 12.7 File Saving

Feature owners: `Report.save`, `save_report`, `mkforge.assets`

Behavior:

1. Validate the object is a `Report`.
2. Validate the destination path.
3. Collect local image paths.
4. Raise `MissingAssetError` if any local image is absent.
5. Render Markdown.
6. Optionally copy or download images.
7. Optionally rewrite image links.
8. Create parent directories.
9. Write UTF-8 Markdown.

### 12.8 Asset Bundling

Feature owners: `save_report(copy_assets=True)`,
`copy_assets_to_dir`, `download_assets_to_dir`, `rewrite_image_paths`

Behavior:

- local images are copied to `assets/` next to the Markdown file;
- remote images are downloaded into the same directory;
- duplicate sources are copied or downloaded once;
- filename collisions are renamed with `_N`;
- collisions emit `UserWarning`;
- image references are rewritten to `assets/<filename>`;
- remote downloads validate scheme and host before network access.

### 12.9 Markdown Verification

Feature owners: `verify_markdown`, `verify_markdown_file`,
`VerificationReport`

Behavior:

- built-in Markdown, GFM, and MkForge resource rules run in one pass;
- custom rules run after built-in rules;
- disabled rules are filtered after diagnostics are produced;
- diagnostics are sorted by `(line, column, rule_id)`;
- `VerificationReport.passed` is `True` when no diagnostics remain.

### 12.10 Settings Discovery

Feature owners: `VerificationSettings`, `verify_markdown_file`,
`verify_markdown(source_path=...)`

Behavior:

- explicit `settings` always wins;
- when settings are omitted and `source_path` is available, MkForge discovers
  TOML settings from nearby files;
- disabled rule IDs are normalized for matching;
- rule option mappings are merged over defaults.

### 12.11 Markdown Validation

Feature owners: validation functions in `mkforge.validation`

Behavior:

- validation functions return booleans for content contracts;
- validation is intentionally separate from verification diagnostics;
- YAML validation checks frontmatter shape and values;
- chapter validation checks H2 order;
- heading validation checks heading level and title;
- image validation checks local and remote image targets.

---

## 13. UML: Public Object Model

```plantuml
@startuml public-object-model
skinparam classAttributeIconSize 0

class Report {
  +title: str
  +children: list[Chapter]
  +metadata: dict | None
  +toc: bool
  +auto_numbering: bool
  +add(*chapters): Report
  +render(): str
  +save(path): None
}

class Chapter {
  +title: str
  +children: list
  +add(*items): Chapter
}

class Section {
  +title: str
  +children: list
  +add(*items): Section
}

class Paragraph { +content: str | tuple }
class Text { +content: str; +style: TextStyle }
class LineBreak
class Link { +url: str; +text: str; +title: str }
class CodeBlock { +code: str; +language: str }
class Table { +headers: tuple; +rows: tuple }
class BulletList { +items: tuple }
class NumberedList { +items: tuple }
class Image { +path: str; +alt: str; +title: str }
class HorizontalRule
class BlockQuote { +content: str }

Report "1" --> "*" Chapter
Chapter "1" --> "*" Section
Chapter "1" --> "*" Paragraph
Chapter "1" --> "*" CodeBlock
Chapter "1" --> "*" Table
Chapter "1" --> "*" BulletList
Chapter "1" --> "*" NumberedList
Chapter "1" --> "*" Image
Chapter "1" --> "*" HorizontalRule
Chapter "1" --> "*" BlockQuote
Section "1" --> "*" Section
Section "1" --> "*" Paragraph
Section "1" --> "*" CodeBlock
Section "1" --> "*" Table
Section "1" --> "*" BulletList
Section "1" --> "*" NumberedList
Section "1" --> "*" Image
Section "1" --> "*" HorizontalRule
Section "1" --> "*" BlockQuote
Paragraph "1" --> "*" Text
Paragraph "1" --> "*" LineBreak
Paragraph "1" --> "*" Link
@enduml
```

## 14. UML: Verification Type Model

```plantuml
@startuml verification-types
skinparam classAttributeIconSize 0

interface MarkdownRule <<type alias>> {
  __call__(source: MarkdownSource): tuple[Diagnostic, ...]
}

class MarkdownSource {
  +text: str
  +lines: tuple[MarkdownLine, ...]
  +path: Path | None
  +settings: VerificationSettings
  +from_text(...): MarkdownSource
  +rule_options(rule_id): dict
}

class MarkdownLine {
  +number: int
  +text: str
}

class VerificationSettings {
  +disabled: frozenset[str]
  +rules: dict[str, RuleOptions]
  +rule_options(rule_id): RuleOptions
}

class VerificationReport {
  +rule_set_name: str
  +diagnostics: tuple[Diagnostic, ...]
  +passed: bool
}

class Diagnostic {
  +rule_id: str
  +name: str
  +line: int
  +column: int
  +message: str
  +category: str
  +severity: str
}

MarkdownSource --> MarkdownLine
MarkdownSource --> VerificationSettings
VerificationReport --> Diagnostic
MarkdownRule ..> MarkdownSource : receives
MarkdownRule ..> Diagnostic : returns
@enduml
```

## 15. UML: Module Architecture

```plantuml
@startuml module-architecture
skinparam linetype ortho
left to right direction

package "mkforge (public)" {
  [__init__]
}

package "Report generation" {
  [document]
  [content]
  [rendering]
  [assets]
  [errors]
  [input_checks]
}

package "Verification" {
  [verification.api]
  [verification.policy]
  [verification.registry]
  [verification.settings]
  [rules.markdown]
  [rules.gfm]
}

package "Validation" {
  [validation]
  [validation.markdown_contracts]
}

[__init__] --> [document]
[__init__] --> [content]
[__init__] --> [errors]
[__init__] --> [verification.api]
[__init__] --> [validation]

[document] --> [content]
[document] --> [errors]
[document] --> [input_checks]
[document] ..> [rendering] : lazy import

[rendering] --> [content]
[rendering] --> [input_checks]
[rendering] ..> [assets] : lazy import
[assets] --> [errors]

[verification.api] --> [verification.registry]
[verification.api] --> [verification.policy]
[verification.api] --> [verification.settings]
[verification.registry] --> [verification.policy]
[verification.registry] --> [rules.markdown]
[verification.registry] --> [rules.gfm]
[validation] --> [validation.markdown_contracts]
[validation.markdown_contracts] --> [verification.source_scan]
@enduml
```

## 16. UML: Render Sequence

```plantuml
@startuml render-sequence
participant User
participant Report
participant Rendering
participant Assets

User -> Report: render()
Report -> Rendering: render_report(report)
Rendering -> Rendering: _render_metadata(dict)
note right: YAML frontmatter block
Rendering -> Rendering: append H1 title
Rendering -> Rendering: _generate_toc(report)
note right: TOC lines or ""
loop chapters and sections
  Rendering -> Rendering: render_content_element(item)
  note right: item.render() via Renderable protocol
end
Rendering --> Report: complete document str
Report --> User: str

User -> Report: save(path, copy_assets=True)
Report -> Rendering: save_report(report, path, copy_assets=True)
Rendering -> Assets: collect_local_image_paths(report)
Rendering -> Assets: verify_assets(paths)
note right: MissingAssetError if absent
Rendering -> Rendering: render_report(report)
Rendering -> Assets: copy_assets_to_dir(local_paths, assets_dir)
Rendering -> Assets: collect_remote_image_urls(report)
Rendering -> Assets: download_assets_to_dir(urls, assets_dir)
note right: DownloadAssetError on failure
Rendering -> Assets: rewrite_image_paths(markdown, local_map, remote_map)
Rendering -> Rendering: write UTF-8 file
@enduml
```

## 17. UML: Verification Sequence

```plantuml
@startuml verification-sequence
participant User
participant "verify_markdown" as API
participant Registry
participant Rule
participant VerificationReport

User -> API: verify_markdown(text, settings, custom_rules)
API -> API: resolve settings
API -> API: MarkdownSource.from_text(...)
API -> Registry: MARKDOWN_COMPLIANCE.rules
loop each built-in rule
  API -> Rule: rule(source)
  Rule --> API: tuple[Diagnostic, ...]
end
loop each custom rule
  API -> Rule: rule(source)
  Rule --> API: tuple[Diagnostic, ...]
end
API -> API: filter disabled
API -> API: sort by (line, col, rule_id)
API -> VerificationReport: new VerificationReport
VerificationReport --> User: report
@enduml
```

## 18. UML: Validation Flow

```plantuml
@startuml validation-flow
start
:add(item) called on Report / Chapter / Section;
if (container is Report?) then (yes)
  if (item is Chapter?) then (yes)
    :append child;
  else (no)
    :raise InvalidChildError;
  endif
else (no)
  if (item is Section or content element?) then (yes)
    :append child;
  else (no)
    :raise InvalidChildError;
  endif
endif
stop
@enduml
```

### 18.1 UML: Markdown Validation Sequence

```plantuml
@startuml markdown-validation-sequence
participant User
participant "validate_markdown_yaml" as YAML
participant "validate_markdown_chapters" as Chapters
participant "validate_markdown_headings" as Headings
participant "validate_markdown_images" as Images
participant "validation.markdown_contracts" as Contracts

User -> YAML: markdown, expected, strict
YAML -> Contracts: parse frontmatter
Contracts --> YAML: bool
YAML --> User: bool

User -> Chapters: markdown, expected, strict
Chapters -> Contracts: extract H2 headings
Contracts --> Chapters: bool
Chapters --> User: bool

User -> Headings: markdown, expected pairs, strict
Headings -> Contracts: extract heading level/title pairs
Contracts --> Headings: bool
Headings --> User: bool

User -> Images: markdown, base_path, timeout
Images -> Contracts: extract image targets
Contracts -> Contracts: local exists or safe HTTP(S) reachable
Contracts --> Images: bool
Images --> User: bool
@enduml
```

## 19. Complete Demos

### Report generation

```bash
uv run python demo_report.py
```

Exercises: dictionary metadata, TOC, automatic numbering, H1-H6 headings,
paragraphs and inline styles, tables, bullet and numbered lists, images,
block quotes, horizontal rules, code blocks, file saving.

### Verification

```bash
uv run python demo_verif.py
```

Exercises: clean GFM source, mixed conformance violations, markdownlint-derived
rules, file verification with resource checks, custom rules, disabled rules,
rule option overrides, multiple custom rules, virtual `source_path`.

### Validation

```bash
uv run python demo_validation.py
```

Exercises: YAML frontmatter contracts, strict and minimum matching, H2 chapter
order checks, heading level/title checks, local image existence, remote HTTP(S)
image checks, and a combined boolean validation gate.
