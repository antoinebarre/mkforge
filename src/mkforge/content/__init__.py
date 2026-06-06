"""Markdown content elements for report composition.

Exports every inline and block element that can appear inside a Chapter or
Section.  Each element type is defined in its own module together with its
construction-time validation and ``render() -> str`` method.

All content types are immutable frozen dataclasses so that report trees are
deterministic and side-effect free.
"""

from __future__ import annotations

from mkforge.content._base import Renderable
from mkforge.content.code import CodeBlock
from mkforge.content.image import Image
from mkforge.content.lists import BulletList, NumberedList
from mkforge.content.misc import BlockQuote, HorizontalRule
from mkforge.content.paragraph import Paragraph
from mkforge.content.table import Table
from mkforge.content.text import LineBreak, Link, Text, TextStyle

type ContentElement = (
    Paragraph
    | Text
    | CodeBlock
    | Table
    | BulletList
    | NumberedList
    | Image
    | HorizontalRule
    | BlockQuote
)

CONTENT_TYPES = (
    Paragraph,
    Text,
    CodeBlock,
    Table,
    BulletList,
    NumberedList,
    Image,
    HorizontalRule,
    BlockQuote,
)

__all__ = [
    "CONTENT_TYPES",
    "BlockQuote",
    "BulletList",
    "CodeBlock",
    "ContentElement",
    "HorizontalRule",
    "Image",
    "LineBreak",
    "Link",
    "NumberedList",
    "Paragraph",
    "Renderable",
    "Table",
    "Text",
    "TextStyle",
]
