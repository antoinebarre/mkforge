"""Markdown renderers for leaf report nodes."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from mkforge.leaves import (
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

type BlockRenderer = Callable[[object], str]


def render_leaf(node: object) -> str:
    """Render a leaf node.

    Args:
        node: Leaf node to render.

    Returns:
        Rendered Markdown block.
    """
    renderer = _BLOCK_RENDERERS.get(type(node))
    if renderer is None:
        message = f"Unknown node type: {type(node).__name__}"
        raise TypeError(message)
    return renderer(node)


def _render_paragraph(node: object) -> str:
    """Render a paragraph node."""
    paragraph = cast("Paragraph", node)
    if isinstance(paragraph.content, str):
        return paragraph.content
    return "".join(_render_inline(item) for item in paragraph.content)


def _render_inline(node: Text | LineBreak) -> str:
    """Render one inline node."""
    if isinstance(node, Text):
        return _render_text(node)
    return "  \n"


def _render_text(node: Text) -> str:
    """Render a text node."""
    return _TEXT_RENDERERS[node.style](node.content)


def _plain(value: str) -> str:
    """Render plain text."""
    return value


def _bold(value: str) -> str:
    """Render bold text."""
    return f"**{value}**"


def _italic(value: str) -> str:
    """Render italic text."""
    return f"*{value}*"


def _code(value: str) -> str:
    """Render inline code text."""
    return f"`{value}`"


def _strikethrough(value: str) -> str:
    """Render strikethrough text."""
    return f"~~{value}~~"


def _render_code_block(node: object) -> str:
    """Render a fenced code block."""
    block = cast("CodeBlock", node)
    fence = f"```{block.language}" if block.language else "```"
    return f"{fence}\n{block.code}\n```"


def _render_table(node: object) -> str:
    """Render a GFM table."""
    table = cast("Table", node)
    rows = [_table_row(table.headers), _table_separator(table.headers)]
    rows.extend(_table_row(row) for row in table.rows)
    return "\n".join(rows)


def _table_row(cells: tuple[str, ...]) -> str:
    """Render one table row."""
    return "| " + " | ".join(cells) + " |"


def _table_separator(headers: tuple[str, ...]) -> str:
    """Render the table header separator."""
    return "| " + " | ".join("---" for _header in headers) + " |"


def _render_bullet_list(node: object) -> str:
    """Render an unordered list."""
    bullet_list = cast("BulletList", node)
    return "\n".join(f"- {item}" for item in bullet_list.items)


def _render_numbered_list(node: object) -> str:
    """Render an ordered list."""
    numbered_list = cast("NumberedList", node)
    return "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(numbered_list.items, start=1)
    )


def _render_image(node: object) -> str:
    """Render an image reference."""
    image = cast("Image", node)
    title = f' "{image.title}"' if image.title else ""
    return f"![{image.alt}]({image.path}{title})"


def _render_quote(node: object) -> str:
    """Render a block quote."""
    quote = cast("BlockQuote", node)
    return "\n".join(f"> {line}" for line in quote.content.splitlines())


def _render_text_block(node: object) -> str:
    """Render a top-level text node."""
    return _render_text(cast("Text", node))


def _render_rule(_node: object) -> str:
    """Render a horizontal rule."""
    return "---"


_TEXT_RENDERERS: dict[str, Callable[[str], str]] = {
    "plain": _plain,
    "bold": _bold,
    "italic": _italic,
    "code": _code,
    "strikethrough": _strikethrough,
}
_BLOCK_RENDERERS: dict[type[object], BlockRenderer] = {
    Paragraph: _render_paragraph,
    Text: _render_text_block,
    CodeBlock: _render_code_block,
    Table: _render_table,
    BulletList: _render_bullet_list,
    NumberedList: _render_numbered_list,
    Image: _render_image,
    HorizontalRule: _render_rule,
    BlockQuote: _render_quote,
}
