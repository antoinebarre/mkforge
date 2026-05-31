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
from mkforge.diagnostics import (
    Diagnostic,
    FunctionRule,
    RuleRegistry,
    SourceContext,
)
from mkforge.document import Report
from mkforge.errors import (
    InvalidChildError,
    InvalidTableError,
    ReportDepthError,
)
from mkforge.headings import Chapter, Section
from mkforge.validation import Validator, validate, validate_file
from mkforge.verification import Verifier, verify, verify_file

__all__ = [
    "PROJECT_DESCRIPTION",
    "PROJECT_NAME",
    "BlockQuote",
    "BulletList",
    "Chapter",
    "CodeBlock",
    "Diagnostic",
    "FunctionRule",
    "HorizontalRule",
    "Image",
    "InvalidChildError",
    "InvalidTableError",
    "LineBreak",
    "NumberedList",
    "Paragraph",
    "Report",
    "ReportDepthError",
    "RuleRegistry",
    "Section",
    "SourceContext",
    "Table",
    "Text",
    "Validator",
    "Verifier",
    "validate",
    "validate_file",
    "verify",
    "verify_file",
]
