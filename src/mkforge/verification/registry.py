"""Markdown conformance policy registry.

This module assembles the built-in Markdown and GFM conformance policy from
rule modules. It is the single place that couples the rule registry to the
policy type, keeping policy.py free of concrete rule dependencies.
"""

from __future__ import annotations

from mkforge.verification.policy import (
    MarkdownPolicy,
    MarkdownRule,
)
from mkforge.verification.rules.gfm import (
    gfm001_table_delimiter,
    gfm002_table_column_count,
    gfm003_task_list_marker,
)
from mkforge.verification.rules.markdown import (
    markdownlint_remaining,
    md011_reversed_link_syntax,
    md018_atx_heading_space,
    md020_closed_atx_heading_space,
    md034_bare_url,
    md037_emphasis_marker_space,
    md038_code_span_space,
    md039_link_text_space,
    mkf001_local_resource_exists,
)


def markdown_compliance_policy() -> MarkdownPolicy:
    """Return the merged Markdown and GFM conformance policy.

    Returns:
        Policy containing all built-in conformance rules.
    """
    return MarkdownPolicy(
        name="markdown-compliance",
        rules=(*_markdown_rules(), *_gfm_rules()),
    )


def _markdown_rules() -> tuple[MarkdownRule, ...]:
    """Return classic Markdown conformance rule callables.

    Returns:
        Classic Markdown rule callables.
    """
    return (
        markdownlint_remaining.check,
        md011_reversed_link_syntax.check,
        md018_atx_heading_space.check,
        md020_closed_atx_heading_space.check,
        md034_bare_url.check,
        md037_emphasis_marker_space.check,
        md038_code_span_space.check,
        md039_link_text_space.check,
        mkf001_local_resource_exists.check,
    )


def _gfm_rules() -> tuple[MarkdownRule, ...]:
    """Return GitHub Flavored Markdown conformance rule callables.

    Returns:
        GFM rule callables.
    """
    return (
        gfm001_table_delimiter.check,
        gfm002_table_column_count.check,
        gfm003_task_list_marker.check,
    )


MARKDOWN_COMPLIANCE = markdown_compliance_policy()
