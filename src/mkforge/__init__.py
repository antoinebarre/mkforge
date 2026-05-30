"""Programmatic Markdown report generation for Python."""

from mkforge._metadata import PROJECT_DESCRIPTION, PROJECT_NAME
from mkforge.errors import (
    InvalidChildError,
    InvalidTableError,
    ReportDepthError,
)
from mkforge.nodes import (
    BlockQuote,
    BulletList,
    Chapter,
    CodeBlock,
    HorizontalRule,
    Image,
    LineBreak,
    Metadata,
    NumberedList,
    Paragraph,
    Report,
    Section,
    Table,
    Text,
)

__all__ = [
    "PROJECT_DESCRIPTION",
    "PROJECT_NAME",
    "BlockQuote",
    "BulletList",
    "Chapter",
    "CodeBlock",
    "HorizontalRule",
    "Image",
    "InvalidChildError",
    "InvalidTableError",
    "LineBreak",
    "Metadata",
    "NumberedList",
    "Paragraph",
    "Report",
    "ReportDepthError",
    "Section",
    "Table",
    "Text",
]
