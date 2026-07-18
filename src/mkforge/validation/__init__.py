"""Project-specific Markdown validation helpers.

Validation checks whether a Markdown document satisfies caller-defined
contracts such as required YAML frontmatter, H2 chapter order, heading
level/title order, and image reachability.  This is separate from Markdown/GFM
verification, which checks syntax and compliance rules.
"""

from mkforge.validation.markdown_contracts import (
    diagnose_markdown_chapters,
    diagnose_markdown_headings,
    diagnose_markdown_images,
    diagnose_markdown_yaml,
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)

__all__ = [
    "diagnose_markdown_chapters",
    "diagnose_markdown_headings",
    "diagnose_markdown_images",
    "diagnose_markdown_yaml",
    "validate_markdown_chapters",
    "validate_markdown_headings",
    "validate_markdown_images",
    "validate_markdown_yaml",
]
