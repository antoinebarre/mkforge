# Software Requirements Specification

## 1. Identification

Document ID: `MKF-SRS-001`

Product: MkForge

Version: 0.1.0

Status: Baseline for implementation and verification

Primary audience: developers, reviewers, maintainers, and qualification
auditors.

## 2. Purpose

This Software Requirements Specification defines the externally observable
requirements for MkForge. MkForge is a Python package that generates GitHub
Flavored Markdown reports from structured Python objects.

The requirements are written to be reviewable, testable, and traceable to
implementation modules and verification assets.

## 3. Scope

MkForge shall provide a programmatic API for building Markdown reports.

MkForge shall include:

- a report root;
- hierarchical chapters and sections;
- Markdown content elements;
- dictionary-based YAML frontmatter;
- table of contents generation;
- automatic heading numbering;
- string rendering and file saving;
- Markdown conformance verification;
- Markdown contract validation helpers;
- explicit validation errors.

MkForge shall not include:

- HTML, PDF, or static site generation;
- Markdown project scanning;
- external image copying;
- CI execution;
- a fixed metadata schema.

## 4. References

| ID | Reference |
|---|---|
| REF-001 | GitHub Flavored Markdown table and heading syntax |
| REF-002 | Python 3.12 standard library |
| REF-003 | Repository `AGENTS.md` coding and quality requirements |
| REF-004 | `make check` repository verification command |
| REF-005 | Scribpy report generator documentation used as initial inspiration |

## 5. Terms And Definitions

| Term | Definition |
|---|---|
| Report | Root object representing one generated Markdown document. |
| Chapter | Top-level report division rendered below the document title. |
| Section | Nested heading container inside a chapter or another section. |
| Content element | Markdown-renderable item such as paragraph, table, list, image, code block, rule, quote, or text. |
| GFM | GitHub Flavored Markdown. |
| Frontmatter | YAML-like metadata block delimited by `---` fences. |
| TOC | Table of contents containing anchor links to chapters and sections. |
| Qualification evidence | Tests, checks, traceability, and deterministic behavior supporting review and acceptance. |

## 6. Operating Environment

MkForge shall run on Python 3.12 or later.

MkForge runtime code shall use only the Python standard library.

MkForge shall be usable from scripts, CI jobs, and other Python packages without
requiring a project configuration file.

## 7. Assumptions

| ID | Assumption |
|---|---|
| ASM-001 | The caller is responsible for choosing semantically correct report content. |
| ASM-002 | Image paths are rendered as provided and are not validated or copied during rendering. |
| ASM-003 | Markdown consumers are responsible for resolving generated GFM anchors. |
| ASM-004 | Metadata dictionaries preserve insertion order as guaranteed by Python 3.12 dictionaries. |
| ASM-005 | Remote image validation depends on external network access and remote server behavior. |

## 8. Constraints

| ID | Constraint |
|---|---|
| CON-001 | Runtime dependencies shall be limited to the Python standard library. |
| CON-002 | Public APIs exported from `mkforge` shall remain narrow and explicit. |
| CON-003 | Generated Markdown shall be deterministic for identical input objects. |
| CON-004 | Functions and modules shall remain small enough to satisfy repository complexity and logical line-count gates. |
| CON-005 | The document title shall be the only level-1 Markdown heading. |

## 9. External Interfaces

### 9.1 Python API

The package shall expose the public names listed in section 14 from
`mkforge.__init__`.

### 9.2 File System Interface

`Report.save(path)` shall write UTF-8 Markdown to the given path and create
missing parent directories.

### 9.3 Markdown Output Interface

`Report.render()` and `mkforge.rendering.render_report(report)` shall return a
single Markdown string.

### 9.4 Markdown Validation Interface

`mkforge.validation` shall expose boolean helpers that evaluate Markdown source
text against caller-supplied contracts.

## 10. Functional Requirements

### SRS-FR-001 Report Root

MkForge shall expose a `Report` class as the document root.

Acceptance criteria:

- `Report(title="Example")` creates a report.
- A blank report title raises `ValueError`.
- `Report.render()` returns Markdown text.
- `Report.save(path)` writes Markdown to disk.

### SRS-FR-002 Report Metadata

`Report.metadata` shall accept `None` or `dict[str, object]`.

Acceptance criteria:

- When metadata is `None`, no frontmatter block is rendered.
- When metadata is a dictionary, each key is rendered in insertion order.
- Scalar values render as `key: value`.
- Boolean values render as `true` or `false`.
- `None` values render as `null`.
- `list` and `tuple` values render as YAML list items.
- MkForge shall not define, require, or validate fixed metadata keys.

### SRS-FR-003 Report Title Heading

The report title shall be rendered as the only level-1 Markdown heading.

Acceptance criteria:

- The rendered document contains `# {report.title}`.
- Chapters shall not render as level-1 headings.

### SRS-FR-004 Chapter Composition

MkForge shall expose a `Chapter` class for top-level report divisions.

Acceptance criteria:

- `Report.add(chapter)` accepts `Chapter`.
- `Report.add(non_chapter)` raises `InvalidChildError`.
- A blank chapter title raises `ValueError`.
- A chapter renders as `## {title}`.
- `Chapter.add(*items)` returns the same `Chapter` instance.

### SRS-FR-005 Section Composition

MkForge shall expose a `Section` class for nested report headings.

Acceptance criteria:

- `Chapter.add(section)` accepts `Section`.
- `Section.add(section)` accepts nested `Section`.
- `Chapter.add(content)` and `Section.add(content)` accept supported content elements.
- Unsupported children raise `InvalidChildError`.
- A blank section title raises `ValueError`.
- Direct child sections render as level-3 headings.
- Nested sections increment heading level by one.
- Rendering deeper than H6 raises `ReportDepthError`.

### SRS-FR-006 Paragraph Content

MkForge shall expose `Paragraph`.

Acceptance criteria:

- `Paragraph("text")` renders `text`.
- `Paragraph("")` raises `ValueError`.
- `Paragraph((Text(...), LineBreak(), ...))` renders inline content in order.
- `Paragraph((Link(...), ...))` accepts `Link` inline elements.

### SRS-FR-007 Inline Text Content

MkForge shall expose `Text`, `LineBreak`, and `Link`.

Acceptance criteria:

- `Text("x")` renders `x`.
- `Text("x", style="bold")` renders `**x**`.
- `Text("x", style="italic")` renders `*x*`.
- `Text("x", style="code")` renders `` `x` ``.
- `Text("x", style="strikethrough")` renders `~~x~~`.
- `LineBreak()` inside a paragraph renders a GFM hard line break.
- `Link(url, text)` renders `[text](url)`.
- `Link(url, text, title)` renders `[text](url "title")`.
- `Link(url)` with empty text renders `[](url)`.
- `Link` is valid only inside a `Paragraph` inline tuple.

### SRS-FR-008 Code Blocks

MkForge shall expose `CodeBlock`.

Acceptance criteria:

- `CodeBlock("x")` renders a fenced code block.
- `CodeBlock("x", language="python")` includes the language hint in the opening fence.

### SRS-FR-009 Tables

MkForge shall expose `Table`.

Acceptance criteria:

- A table with headers renders a GFM pipe table.
- `Table.from_columns()` accepts column-oriented data and renders equivalent
  GFM rows.
- Empty headers raise `InvalidTableError`.
- Any row whose width differs from the header width raises `InvalidTableError`.
- Any `from_columns` column whose length differs from the others raises
  `InvalidTableError`.
- Non-tuple headers, rows, or row values raise `TypeError` with field context.
- Non-mapping `from_columns` input or non-tuple column values raise
  `TypeError` with field context.
- Non-string cells raise `TypeError` with field and index context.

### SRS-FR-010 Lists

MkForge shall expose `BulletList` and `NumberedList`.

Acceptance criteria:

- `BulletList(("a", "b"))` renders `- a` and `- b`.
- `NumberedList(("a", "b"))` renders `1. a` and `2. b`.
- Empty item tuples raise `ValueError`.

### SRS-FR-011 Images

MkForge shall expose `Image`.

Acceptance criteria:

- `Image(path, alt)` renders `![alt](path)`.
- If `title` is set, the title is included in the Markdown image syntax.
- `save()` verifies that all local image paths exist before writing; missing
  paths raise `MissingAssetError`.
- `save(path, copy_assets=True)` copies local images into `assets/` next to
  the output file and rewrites the image links accordingly.
- `save(path, copy_assets=True)` downloads remote image URLs into `assets/`;
  download failures raise `DownloadAssetError`.
- Filename collisions on copy or download are resolved by renaming with a
  `_N` suffix and emitting a `UserWarning`.

### SRS-FR-012 Block Quotes

MkForge shall expose `BlockQuote`.

Acceptance criteria:

- Each line in `BlockQuote.content` renders with a `> ` prefix.

### SRS-FR-013 Horizontal Rules

MkForge shall expose `HorizontalRule`.

Acceptance criteria:

- `HorizontalRule()` renders `---`.

### SRS-FR-014 Table Of Contents

When `Report.toc` is true, MkForge shall render a table of contents after the
report title and before chapters.

Acceptance criteria:

- The TOC includes chapters and sections.
- TOC indentation reflects nesting.
- TOC anchors are lower-case, punctuation-stripped, and hyphenated.
- An empty report does not render an empty TOC block.

### SRS-FR-015 Automatic Numbering

When `Report.auto_numbering` is true, MkForge shall prefix chapter and section
headings with dotted hierarchical numbers.

Acceptance criteria:

- The first chapter renders as `## 1. Title`.
- The first direct section in that chapter renders as `### 1.1. Title`.
- Stored titles remain unchanged.
- Numbering resets per sibling level.

### SRS-FR-016 Public Render Functions

MkForge shall expose module-level render helpers in `mkforge.rendering`.

Acceptance criteria:

- `render_report(report)` returns the same output as `report.render()`.
- `save_report(report, path)` writes the same output as `report.save(path)`.
- `save_report(report, path, copy_assets=True)` is equivalent to
  `report.save(path, copy_assets=True)`.

### SRS-FR-017 Helper Functions

MkForge shall provide deterministic helper functions for anchors and numbering.

Acceptance criteria:

- `anchor_slug(title)` returns the documented GFM-style slug.
- `numbered_title(title, context)` prefixes a title with the active context.

### SRS-FR-018 Defensive Input Validation

MkForge shall validate public constructor and rendering inputs before they can
cause unplanned `AttributeError`, `KeyError`, or low-context Python failures.

Acceptance criteria:

- Non-string titles raise `TypeError` with the affected title field.
- Non-dictionary metadata raises `TypeError`.
- Non-string metadata keys raise `TypeError`.
- Non-boolean `toc` or `auto_numbering` flags raise `TypeError`.
- Invalid initial `children` collections raise `TypeError` or `InvalidChildError`.
- Invalid paragraph inline content raises `TypeError`.
- Invalid `Text.style` raises `ValueError`.
- Invalid save paths raise `TypeError` or `ValueError`.
- `render_report(non_report)` raises `TypeError`.

## 11. Non-Functional Requirements

### SRS-NFR-001 Determinism

For identical report objects, MkForge shall produce identical Markdown output.

### SRS-NFR-002 Type Safety

The package shall pass strict `mypy` checks configured by the repository.

### SRS-NFR-003 Code Quality

The package shall pass formatting, linting, Flake8, docstring, complexity, and
logical line-count checks through `make check`.

### SRS-NFR-004 Test Coverage

The package shall maintain 100% test coverage for `src/mkforge`.

### SRS-NFR-005 Security

The package shall pass repository Bandit and dependency audit checks.

### SRS-NFR-006 Dependency Control

Runtime code shall introduce no third-party dependencies.

### SRS-NFR-007 Documentation

The repository shall include:

- this SRS;
- a Software Design Description;
- an API reference with examples;
- UML diagrams explaining object model, modules, and rendering flow;
- runnable `demo_report.py`, `demo_verif.py`, and `demo_validation.py`
  scripts.

## 12. Data Requirements

| Data Item | Type | Validation | Rendering |
|---|---|---|---|
| Report title | `str` | non-blank | `# title` |
| Report metadata | `dict[str, object] | None` | none beyond type hints | YAML frontmatter |
| Chapter title | `str` | non-blank | `## title` |
| Section title | `str` | non-blank, depth <= H6 at render | `###` through `######` |
| Paragraph content | `str | tuple[Text | LineBreak | Link, ...]` | empty plain string rejected | Markdown paragraph |
| Link | `url: str`, `text: str`, `title: str` | none | `[text](url)` inline Markdown |
| Text style | literal style string | type checked | inline GFM |
| Table headers | `tuple[str, ...]` | non-empty | GFM header |
| Table rows | `tuple[tuple[str, ...], ...]` | width equals headers | GFM rows |
| Table columns | `Mapping[str, tuple[str, ...]]` | all columns same length | alternate GFM table input |
| List items | `tuple[str, ...]` | non-empty | Markdown list |
| Image path | `str` | not validated during rendering; can be checked by `validate_markdown_images` | Markdown image link |
| Block quote content | `str` | not validated | quoted lines |

## 13. Verification Requirements

Each requirement shall be verified by one or more of:

- automated unit tests;
- 100% coverage enforcement;
- `make check`;
- demonstration script execution;
- document review.

The authoritative local verification command is:

```bash
make check
```

The demonstration commands are:

```bash
uv run python demo_report.py
uv run python demo_verif.py
uv run python demo_validation.py
```

## 14. Public API

The package shall export these public names from `mkforge`:

| Name | Category |
|---|---|
| `Report` | document root |
| `Chapter` | heading container |
| `Section` | heading container |
| `Paragraph` | content element |
| `Text` | inline content |
| `LineBreak` | inline content |
| `Link` | inline content |
| `CodeBlock` | content element |
| `Table` | content element |
| `BulletList` | content element |
| `NumberedList` | content element |
| `Image` | content element |
| `HorizontalRule` | content element |
| `BlockQuote` | content element |
| `InvalidChildError` | exception |
| `InvalidTableError` | exception |
| `ReportDepthError` | exception |
| `MissingAssetError` | exception |
| `DownloadAssetError` | exception |
| `Diagnostic` | diagnostic object |
| `MarkdownSource` | verification source context |
| `VerificationReport` | verification result |
| `verify_markdown` | verification helper |
| `validate_markdown_yaml` | YAML frontmatter validation helper |
| `validate_markdown_chapters` | chapter order validation helper |
| `validate_markdown_headings` | heading level and title validation helper |
| `validate_markdown_images` | local and remote image validation helper |

## 15. Requirement Traceability Matrix

| Requirement | Implementation | Verification |
|---|---|---|
| SRS-FR-001 | `document.Report` | `tests/test_helpers.py`, `tests/test_validation.py` |
| SRS-FR-002 | `rendering._render_metadata`, `document.Report` | `tests/test_report_generation.py`, `tests/test_helpers.py` |
| SRS-FR-003 | `rendering._report_blocks` | `tests/test_report_generation.py`, demo output |
| SRS-FR-004 | `document.Chapter`, `document.Report.add` | `tests/test_validation.py`, `tests/test_helpers.py` |
| SRS-FR-005 | `document.Section`, `document.compute_section_heading_level` | `tests/test_report_generation.py`, `tests/test_validation.py` |
| SRS-FR-006 | `content.Paragraph`, `rendering._render_paragraph` | `tests/test_report_generation.py`, `tests/test_validation.py` |
| SRS-FR-007 | `content.Text`, `content.LineBreak`, `rendering._render_inline` | `tests/test_report_generation.py` |
| SRS-FR-008 | `content.CodeBlock`, `rendering._render_code_block` | `tests/test_report_generation.py` |
| SRS-FR-009 | `content.Table`, `rendering._render_table` | `tests/test_report_generation.py`, `tests/test_validation.py` |
| SRS-FR-010 | `content.BulletList`, `content.NumberedList` | `tests/test_report_generation.py`, `tests/test_validation.py` |
| SRS-FR-011 | `content.Image`, `rendering._render_image` | `tests/test_report_generation.py`, `demo_report.py` |
| SRS-FR-012 | `content.BlockQuote`, `rendering._render_block_quote` | `tests/test_report_generation.py` |
| SRS-FR-013 | `content.HorizontalRule`, `rendering._render_horizontal_rule` | `tests/test_report_generation.py` |
| SRS-FR-014 | `rendering._generate_toc` | `tests/test_report_generation.py`, `tests/test_helpers.py` |
| SRS-FR-015 | `rendering.NumberingContext`, `rendering._heading_title` | `tests/test_report_generation.py`, `tests/test_helpers.py` |
| SRS-FR-016 | `rendering.render_report`, `rendering.save_report` | `tests/test_report_generation.py`, `tests/test_helpers.py` |
| SRS-FR-017 | `rendering.anchor_slug` | `tests/test_helpers.py` |
| SRS-FR-018 | `content._validate_*`, `document._validate_*`, `input_checks.*` | `tests/test_validation.py` |
| SRS-FR-019 | `verification` | `tests/test_markdown_verification.py` |
| SRS-FR-020 | `MarkdownRule`, `VerificationSettings` | `tests/test_markdown_verification.py` |
| SRS-FR-021 | `validation.markdown_contracts` | `tests/test_markdown_validation.py`, `demo_validation.py` |
| SRS-NFR-001..007 | package and repository checks | `make check`, demos, document review |

## 16. Open Items

| ID | Item | Disposition |
|---|---|---|
| OPN-001 | YAML escaping is minimal and intentionally not a full YAML serializer. | Documented limitation. |
| OPN-002 | Image file copying is implemented via `copy_assets=True`; remote download is blocked for private/loopback hosts (SSRF protection). | Resolved in current implementation. |
| OPN-003 | Duplicate heading anchors are not disambiguated. | Candidate future requirement. |

## 17. Markdown Verification Requirements

### SRS-FR-019 Verification Diagnostics

MkForge shall provide Markdown diagnostics for Markdown and GFM conformance in
one merged verification pass.

Acceptance criteria:

- `verify_markdown(source)` returns a verification report using the merged
  Markdown/GFM policy.
- File helpers read UTF-8 Markdown and return diagnostics.
- Diagnostics include rule id, name, category, line, column, message, and
  severity.
- Verification rules are grouped under `verification/rules`.
- Each diagnostic rule is implemented in one Python module.
- Rule identifiers use `MDxxx` for markdownlint-compatible compliance checks,
  `GFMxxx` for GitHub Flavored Markdown checks, and `MKFxxx` for
  MkForge-specific checks.

### SRS-FR-020 Verification Extension ICD

MkForge shall provide a public interface for adding verification rules.

Acceptance criteria:

- A custom rule can be passed to `verify_markdown`.
- Custom rules receive a `MarkdownSource`.
- Custom rules return `tuple[Diagnostic, ...]`.
- Custom rules run after built-in verification rules.

### SRS-FR-021 Markdown Validation Contracts

MkForge shall provide boolean helpers for project-specific Markdown validation.

Acceptance criteria:

- `validate_markdown_yaml(markdown, expected)` returns `True` when frontmatter
  contains at least the expected keys with matching values or value types.
- `validate_markdown_yaml(..., strict=True)` returns `True` only when the
  frontmatter keys exactly match the expected keys.
- `validate_markdown_chapters(markdown, expected)` returns `True` when H2
  chapter titles contain the expected titles in order.
- `validate_markdown_chapters(..., strict=True)` returns `True` only when the
  full H2 chapter sequence exactly matches the expected sequence.
- `validate_markdown_headings(markdown, expected)` returns `True` when heading
  `(level, title)` pairs contain the expected pairs in order.
- `validate_markdown_headings(..., strict=True)` returns `True` only when the
  full heading `(level, title)` sequence exactly matches the expected sequence.
- `validate_markdown_images(markdown, base_path=...)` returns `True` only when
  every local Markdown image target exists.
- `validate_markdown_images` checks HTTP(S) image URLs and returns `False` for
  unreachable, private, loopback, unsupported, or hostless remote targets.
- Image validation ignores Markdown image syntax inside fenced code blocks.
- Validation helpers return booleans and do not emit verification diagnostics.
- A runnable `demo_validation.py` shall demonstrate all validation helpers.
