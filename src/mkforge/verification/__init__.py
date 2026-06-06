"""Markdown conformance verification tools."""

from mkforge.verification.api import (
    VerificationReport,
    verify_markdown,
    verify_markdown_file,
)
from mkforge.verification.policy import (
    Diagnostic,
    MarkdownLine,
    MarkdownRule,
    MarkdownSource,
)
from mkforge.verification.settings import VerificationSettings

__all__ = [
    "Diagnostic",
    "MarkdownLine",
    "MarkdownRule",
    "MarkdownSource",
    "VerificationReport",
    "VerificationSettings",
    "verify_markdown",
    "verify_markdown_file",
]
