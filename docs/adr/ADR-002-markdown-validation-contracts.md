# ADR-002: Markdown Validation Contracts

## Status

Accepted

## Context

MkForge already separates Markdown/GFM verification from document validation.
Verification checks syntax and compliance rules.  Validation checks whether a
document satisfies project-specific contracts such as required frontmatter,
chapter structure, and reachable image references.

Users need small boolean helpers that can be used in CI or scripts without
having to inspect diagnostics:

- validate that YAML frontmatter contains expected keys and values;
- validate that H2 chapters are present in the expected order;
- validate that headings match expected `(level, title)` pairs in order;
- validate that every Markdown image target exists locally or remotely.

## Decision

Add a new `mkforge.validation` package exposing four focused functions:

- `validate_markdown_yaml(markdown, expected, strict=False) -> bool`
- `validate_markdown_chapters(markdown, expected, strict=False) -> bool`
- `validate_markdown_headings(markdown, expected, strict=False) -> bool`
- `validate_markdown_images(markdown, base_path=None, timeout=5.0) -> bool`

`strict=False` means "at least this contract".  `strict=True` means "exactly
this contract" for the checked surface:

- YAML strict mode requires the actual frontmatter keys to match the expected
  keys exactly.
- Chapter strict mode requires the document H2 chapter sequence to match the
  expected sequence exactly.
- Heading strict mode requires the document `(level, title)` heading sequence
  to match the expected sequence exactly.

YAML values are parsed with a small standard-library parser that supports the
frontmatter shape MkForge renders: flat scalar keys and simple list values.
Expected values are compared by both type and value.  An expected Python type,
such as `bool`, checks only the parsed value type.

Image validation scans Markdown image references outside fenced code blocks.
Local paths resolve relative to `base_path` when provided, otherwise relative
to the current working directory.  Remote images are checked with HTTP HEAD and
fall back to GET when HEAD is not supported.  URL checks reject non-HTTP(S)
schemes and private or loopback hosts before opening a network connection.

## Design Patterns

- **Strategy**: strict and minimum matching are two matching strategies selected
  by a boolean input while keeping each public function narrow.
- **Adapter**: URL existence is exposed as a boolean validation helper while
  adapting `urllib.request` exceptions into `False`.

## Consequences

The public API remains simple for CI use.  The boolean result intentionally
does not explain failures; detailed diagnostics can be added later through a
separate validation report API without changing these helpers.

The YAML parser is deliberately limited to MkForge frontmatter contracts.  It
does not try to be a complete YAML implementation, avoiding a new dependency.

`demo_validation.py` documents the intended user workflow with runnable
examples for minimum matching, strict matching, heading levels, local images,
remote images, and combined validation gates.

## PlantUML

```plantuml
@startuml
actor User
package "mkforge.validation" {
  class validate_markdown_yaml
  class validate_markdown_chapters
  class validate_markdown_headings
  class validate_markdown_images
}
package "Markdown source" {
  class Frontmatter
  class Headings
  class ImageReferences
}

User --> validate_markdown_yaml
User --> validate_markdown_chapters
User --> validate_markdown_headings
User --> validate_markdown_images
validate_markdown_yaml --> Frontmatter
validate_markdown_chapters --> Headings
validate_markdown_headings --> Headings
validate_markdown_images --> ImageReferences
@enduml
```
