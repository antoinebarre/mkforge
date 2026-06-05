"""Default Markdown verification rule registry."""

from __future__ import annotations

from mkforge.diagnostics.loader import load_rules
from mkforge.diagnostics.rules import RuleRegistry
from mkforge.verification.profiles import (
    ALL_PROFILES,
    GFM_PROFILE,
    MARKDOWN_PROFILE,
)

MARKDOWN_RULES = (
    "mkv001_heading_increment",
    "mkv002_heading_style",
    "mkv003_unordered_list_marker",
    "mkv004_list_indentation",
    "mkv005_unordered_list_indent_size",
    "mkv006_trailing_spaces",
    "mkv007_tabs",
    "mkv008_reversed_link",
    "mkv009_multiple_blank_lines",
    "mkv010_line_length",
    "mkv011_command_prompt",
    "mkv012_atx_missing_space",
    "mkv013_atx_extra_space",
    "mkv014_closed_atx_missing_space",
    "mkv015_closed_atx_extra_space",
    "mkv016_heading_blank_lines",
    "mkv017_indented_heading",
    "mkv018_blockquote_marker_spacing",
    "mkv019_blockquote_blank_line",
    "mkv020_ordered_list_sequence",
    "mkv021_list_marker_spacing",
    "mkv022_fence_blank_lines",
    "mkv023_list_blank_lines",
    "mkv024_inline_html",
    "mkv025_horizontal_rule_style",
    "mkv026_emphasis_spacing",
    "mkv027_code_span_spacing",
    "mkv028_link_text_spacing",
    "mkv029_code_block_style",
    "mkv030_trailing_newline",
    "mkv031_fence_style",
    "mkv032_emphasis_style",
    "mkv033_strong_style",
    "mkv034_reference_defined",
    "mkv035_reference_used",
)

GFM_RULES = (
    "mkg001_bare_url",
    "mkg002_table_pipe_style",
    "mkg003_table_column_count",
    "mkg004_table_blank_lines",
    "mkg005_table_column_spacing",
)


def verification_rule_registry(profile: str = GFM_PROFILE) -> RuleRegistry:
    """Return a registry for the requested verification profile.

    Args:
        profile: Verification profile name.

    Returns:
        A registry for the requested verification profile.
    """
    return load_rules(_module_names(profile))


def _module_names(profile: str) -> tuple[str, ...]:
    """Return diagnostic module names for a profile.

    Args:
        profile: Verification profile name.

    Returns:
        Diagnostic module names for a profile.
    """
    if profile == MARKDOWN_PROFILE:
        return _qualified("base", MARKDOWN_RULES)
    if profile in {GFM_PROFILE, ALL_PROFILES}:
        return (
            *_qualified("base", MARKDOWN_RULES),
            *_qualified("gfm", GFM_RULES),
        )
    message = f"unknown Markdown verification profile: {profile!r}."
    raise ValueError(message)


def _qualified(group: str, names: tuple[str, ...]) -> tuple[str, ...]:
    """Return fully qualified rule module names.

    Args:
        group: Rule group package name.
        names: Rule module names.

    Returns:
        Fully qualified rule module names.
    """
    prefix = f"mkforge.verification.rules.{group}"
    return tuple(f"{prefix}.{name}" for name in names)
