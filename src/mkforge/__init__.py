"""Programmatic Markdown report generation for Python."""

from mkforge._metadata import PROJECT_DESCRIPTION, PROJECT_NAME
from mkforge.content import (
    BlockQuote,
    BulletList,
    CodeBlock,
    HorizontalRule,
    Image,
    LineBreak,
    NumberedList,
    Paragraph,
    Table,
    Text,
)
from mkforge.document import Report
from mkforge.errors import (
    InvalidChildError,
    InvalidTableError,
    ReportDepthError,
)
from mkforge.headings import Chapter, Section

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
    "NumberedList",
    "Paragraph",
    "Report",
    "ReportDepthError",
    "Section",
    "Table",
    "Text",
]
