"""Programmatic Markdown report generation for Python."""

from mkforge._metadata import PROJECT_DESCRIPTION, PROJECT_NAME
from mkforge.content import (
    BlockQuote,
    BulletList,
    CodeBlock,
    HorizontalRule,
    Image,
    LineBreak,
    Link,
    NumberedList,
    Paragraph,
    Table,
    Text,
)
from mkforge.document import Chapter, Report, Section
from mkforge.errors import (
    DownloadAssetError,
    InvalidChildError,
    InvalidTableError,
    MissingAssetError,
    ReportDepthError,
)
from mkforge.slugify import slugify_heading
from mkforge.validation import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)
from mkforge.verification import (
    Diagnostic,
    MarkdownLine,
    MarkdownRule,
    MarkdownSource,
    VerificationReport,
    VerificationSettings,
    verify_markdown,
    verify_markdown_file,
)

__all__ = [
    "PROJECT_DESCRIPTION",
    "PROJECT_NAME",
    "BlockQuote",
    "BulletList",
    "Chapter",
    "CodeBlock",
    "Diagnostic",
    "DownloadAssetError",
    "HorizontalRule",
    "Image",
    "InvalidChildError",
    "InvalidTableError",
    "LineBreak",
    "Link",
    "MarkdownLine",
    "MarkdownRule",
    "MarkdownSource",
    "MissingAssetError",
    "NumberedList",
    "Paragraph",
    "Report",
    "ReportDepthError",
    "Section",
    "Table",
    "Text",
    "VerificationReport",
    "VerificationSettings",
    "slugify_heading",
    "validate_markdown_chapters",
    "validate_markdown_headings",
    "validate_markdown_images",
    "validate_markdown_yaml",
    "verify_markdown",
    "verify_markdown_file",
]

__version__ = "0.1.0"
