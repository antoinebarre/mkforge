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
from mkforge.markdown_lint_api import (
    FunctionRule,
    MarkdownDiagnostic,
    MarkdownLintContext,
    MarkdownRuleRegistry,
)
from mkforge.markdown_linter import (
    MarkdownLinter,
    lint_markdown,
    lint_markdown_file,
)

__all__ = [
    "PROJECT_DESCRIPTION",
    "PROJECT_NAME",
    "BlockQuote",
    "BulletList",
    "Chapter",
    "CodeBlock",
    "FunctionRule",
    "HorizontalRule",
    "Image",
    "InvalidChildError",
    "InvalidTableError",
    "LineBreak",
    "MarkdownDiagnostic",
    "MarkdownLintContext",
    "MarkdownLinter",
    "MarkdownRuleRegistry",
    "NumberedList",
    "Paragraph",
    "Report",
    "ReportDepthError",
    "Section",
    "Table",
    "Text",
    "lint_markdown",
    "lint_markdown_file",
]
