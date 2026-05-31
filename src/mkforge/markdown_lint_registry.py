"""Default Markdown lint rule registry."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, cast

from mkforge.markdown_lint_api import FunctionRule, MarkdownRuleRegistry

if TYPE_CHECKING:
    from mkforge.markdown_lint_api import RuleCheck

RuleEntry = tuple[str, str, str]

MODULES = {
    "block": "markdown_lint_block_rules",
    "code": "markdown_lint_code_style_rules",
    "doc": "markdown_lint_document_rules",
    "doc_structure": "markdown_lint_document_structure_rules",
    "heading": "markdown_lint_heading_rules",
    "heading_dupes": "markdown_lint_heading_duplicate_rules",
    "inline": "markdown_lint_inline_rules",
    "inline_style": "markdown_lint_inline_style_rules",
    "line": "markdown_lint_line_rules",
    "link_fragment": "markdown_lint_link_fragment_rules",
    "link_style": "markdown_lint_link_style_rules",
    "list_indent": "markdown_lint_list_indent_rules",
    "ordered": "markdown_lint_ordered_list_rules",
    "proper": "markdown_lint_proper_name_rules",
    "ref": "markdown_lint_reference_rules",
    "spacing": "markdown_lint_spacing_rules",
    "structure": "markdown_lint_structure_rules",
    "table": "markdown_lint_table_rules",
    "table_count": "markdown_lint_table_count_rules",
    "table_spacing": "markdown_lint_table_spacing_rules",
    "unordered": "markdown_lint_unordered_list_rules",
}

RULE_ROWS = """
MD001|Heading increment|structure:rule_md001
MD003|Heading style|structure:rule_md003
MD004|Unordered list style|unordered:rule_md004
MD005|List indentation|list_indent:rule_md005
MD007|Unordered list indentation|list_indent:rule_md007
MD009|Trailing spaces|line:rule_md009
MD010|Hard tabs|line:rule_md010
MD011|Reversed link syntax|line:rule_md011
MD012|Multiple blank lines|line:rule_md012
MD013|Line length|line:rule_md013
MD014|Command prompts|block:rule_md014
MD018|No space after hash|heading:rule_md018
MD019|Multiple spaces after hash|heading:rule_md019
MD020|Closed ATX missing space|heading:rule_md020
MD021|Closed ATX multiple spaces|heading:rule_md021
MD022|Blanks around headings|spacing:rule_md022
MD023|Heading start left|heading:rule_md023
MD024|Duplicate heading|heading_dupes:rule_md024
MD025|Single H1|heading_dupes:rule_md025
MD026|Heading punctuation|heading:rule_md026
MD027|Blockquote marker spaces|heading:rule_md027
MD028|Blank line in blockquote|block:rule_md028
MD029|Ordered list prefix|ordered:rule_md029
MD030|List marker space|ordered:rule_md030
MD031|Blanks around fences|block:rule_md031
MD032|Blanks around lists|block:rule_md032
MD033|Inline HTML|inline:rule_md033
MD034|Bare URL|inline:rule_md034
MD035|Horizontal rule style|doc:rule_md035
MD036|Emphasis as heading|doc:rule_md036
MD037|Spaces inside emphasis|inline:rule_md037
MD038|Spaces inside code span|inline:rule_md038
MD039|Spaces inside link text|inline:rule_md039
MD040|Fenced code language|doc:rule_md040
MD041|First line H1|doc_structure:rule_md041
MD042|No empty links|inline:rule_md042
MD043|Required headings|doc_structure:rule_md043
MD044|Proper names|proper:rule_md044
MD045|Image alternate text|inline:rule_md045
MD046|Code block style|code:rule_md046
MD047|Single trailing newline|line:rule_md047
MD048|Code fence style|code:rule_md048
MD049|Emphasis style|inline_style:rule_md049
MD050|Strong style|inline_style:rule_md050
MD051|Link fragments|link_fragment:rule_md051
MD052|Reference links/images|ref:rule_md052
MD053|Reference definitions|ref:rule_md053
MD054|Link image style|link_style:rule_md054
MD055|Table pipe style|table:rule_md055
MD056|Table column count|table_count:rule_md056
MD058|Blanks around tables|table_spacing:rule_md058
MD059|Descriptive link text|inline:rule_md059
MD060|Table column style|table_spacing:rule_md060
"""


def default_markdown_rule_registry() -> MarkdownRuleRegistry:
    """Return the default markdownlint-compatible rule registry."""
    registry = MarkdownRuleRegistry()
    for rule_id, name, path in RULES:
        registry.register(FunctionRule(rule_id, name, _load_rule(path)))
    return registry


def _parse_rule_rows(rows: str) -> tuple[RuleEntry, ...]:
    """Parse compact rule catalog rows."""
    return tuple(
        cast("RuleEntry", tuple(row.split("|", maxsplit=2)))
        for row in rows.splitlines()
        if row.strip()
    )


def _load_rule(path: str) -> RuleCheck:
    """Load one rule function from a compact module path."""
    module_alias, function_name = path.split(":", maxsplit=1)
    module = import_module(f"mkforge.{MODULES[module_alias]}")
    return cast("RuleCheck", getattr(module, function_name))


RULES = _parse_rule_rows(RULE_ROWS)
