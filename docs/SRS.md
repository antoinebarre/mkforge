# Software Requirements Specification

## 1. Purpose

MkForge shall provide a small Python package for generating Markdown reports
from structured Python data. The package is inspired by Scribpy's report
generator documentation while remaining independent from Scribpy's project
builder, parser, and rendering pipeline.

## 2. Scope

MkForge shall generate GitHub Flavored Markdown documents. It shall not build
HTML or PDF artifacts, scan Markdown projects, or execute quality checks.
Those responsibilities remain outside this package.

## 3. Functional Requirements

### SRS-FR-001 Report Root

The package shall expose a `Report` class as the public document root. A report
shall have a non-empty title and zero or more chapters.

### SRS-FR-002 Hierarchical Composition

The package shall expose `Chapter` and `Section` containers. `Report` shall
accept only chapters. `Chapter` and `Section` shall accept nested sections and
leaf content nodes.

### SRS-FR-003 Leaf Content

The package shall support paragraphs, inline text, fenced code blocks, tables,
unordered lists, ordered lists, images, horizontal rules, and block quotes.

### SRS-FR-004 Fluent API

Every container shall expose `add(*items)` and return itself to support fluent
composition.

### SRS-FR-005 Markdown Rendering

`Report.render()` shall return a complete GitHub Flavored Markdown string.
`Report.save(path)` shall create missing parent directories and write UTF-8
Markdown.

### SRS-FR-006 Table of Contents

When `Report.toc` is true, the renderer shall insert a Markdown table of
contents after the report title.

### SRS-FR-007 Automatic Numbering

When `Report.auto_numbering` is true, rendered chapter and section headings
shall receive dotted numbering prefixes without modifying stored titles.

### SRS-FR-008 Validation

The package shall fail fast for invalid child types, empty container titles,
empty table headers, table row width mismatches, empty lists, and section
nesting that would exceed Markdown H6.

## 4. Non-Functional Requirements

### SRS-NFR-001 Dependencies

MkForge shall use the Python standard library only at runtime.

### SRS-NFR-002 Quality

The package shall pass `make check`, including formatting, linting, typing,
metrics, security, tests, and 100% coverage.

### SRS-NFR-003 Maintainability

Functions shall remain small and explicit. Public behavior shall be covered by
tests whose docstrings state the requirement being verified.

## 5. Public API

The package shall export the following names from `mkforge`:

- `Report`
- `Metadata`
- `Chapter`
- `Section`
- `Paragraph`
- `Text`
- `LineBreak`
- `CodeBlock`
- `Table`
- `BulletList`
- `NumberedList`
- `Image`
- `HorizontalRule`
- `BlockQuote`
- `InvalidChildError`
- `InvalidTableError`
- `ReportDepthError`

## 6. Traceability

The initial requirements are derived from Scribpy's report generator manual and
ADR-0008, adapted to MkForge as an independent Markdown report package.
