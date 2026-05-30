# Software Design Description

## 1. Overview

MkForge is implemented as a small object model plus pure rendering functions.
The object model captures report intent. The renderer converts that intent to
GitHub Flavored Markdown.

## 2. Modules

### `mkforge.nodes`

Defines dataclasses for report containers and leaf nodes. Containers own the
fluent `add()` API and validate child types immediately.

### `mkforge.renderer`

Contains pure rendering functions. Rendering is dispatched by concrete node
type through a small table, keeping individual functions focused.

### `mkforge.toc`

Builds GitHub-style anchor slugs and table of contents list items from the
report tree.

### `mkforge.numbering`

Tracks heading counters during traversal and formats dotted heading prefixes.

### `mkforge.errors`

Defines explicit package exceptions for invalid composition, invalid tables,
and unsupported section depth.

## 3. Data Model

`Report` is the root and contains `Chapter` nodes. `Chapter` renders as H1.
`Section` renders as H2 through H6 depending on nesting depth. Leaf nodes render
as Markdown block or inline content.

The model intentionally stores only semantic content. Heading depth, numbering,
TOC anchors, and Markdown syntax are computed during rendering.

## 4. Rendering Flow

1. Render optional metadata frontmatter.
2. Render the report title.
3. Render optional table of contents.
4. Traverse chapters and nested sections.
5. Render leaf nodes through the dispatch table.
6. Join block parts with blank lines.

## 5. Validation Strategy

Validation happens close to the boundary where data enters the model:

- Container titles are checked during construction.
- Child types are checked in `add()`.
- Table shape and list emptiness are checked during construction.
- Section depth is checked when rendering computes the heading level.

## 6. Dependency Strategy

Runtime code uses only the Python standard library. This keeps MkForge suitable
for CI, documentation tooling, and build pipelines that need deterministic
Markdown output without extra runtime installation cost.

## 7. Extension Points

Future releases can add more leaf nodes or renderers by adding dataclasses and
registering their render functions. The current public API remains narrow so
new output formats can be introduced without changing report composition code.
