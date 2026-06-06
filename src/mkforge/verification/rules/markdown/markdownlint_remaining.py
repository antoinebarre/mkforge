"""Markdownlint compatibility facade aggregating all rule modules.

This module delegates to focused rule modules (one per rule or small cohesive
group) and re-exports the private helpers accessed by tests for backward
compatibility. Adding a new rule requires creating a new module and wiring its
``check`` callable here rather than editing this file.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource

# Modules whose dotted names exceed the 79-char line limit are aliased here.
from mkforge.verification.rules.markdown import (
    md005_md006_md007_list_indentation as _m5,
)
from mkforge.verification.rules.markdown import (
    md019_md021_atx_closed_spaces as _m19,
)
from mkforge.verification.rules.markdown import (
    md024_md025_duplicate_headings as _m24,
)
from mkforge.verification.rules.markdown import (
    md031_md032_fence_list_blanks as _m31,
)
from mkforge.verification.rules.markdown import (
    md040_md041_md046_md047_blocks as _m40,
)
from mkforge.verification.rules.markdown._shared import (
    _blank_line_diagnostics,
    _code_filtered_lines,
    _expected_unordered_mark,
    _heading_style_matches,
    _line_is_too_long,
    _previous_line_is_list_item,
)
from mkforge.verification.rules.markdown.md001_heading_increment import (
    check as _check_md001,
)
from mkforge.verification.rules.markdown.md002_first_heading_level import (
    check as _check_md002,
)
from mkforge.verification.rules.markdown.md003_heading_style import (
    check as _check_md003,
)
from mkforge.verification.rules.markdown.md004_unordered_list_style import (
    check as _check_md004,
)
from mkforge.verification.rules.markdown.md009_trailing_spaces import (
    check as _check_md009,
)
from mkforge.verification.rules.markdown.md010_hard_tabs import (
    check as _check_md010,
)
from mkforge.verification.rules.markdown.md012_multiple_blank_lines import (
    check as _check_md012,
)
from mkforge.verification.rules.markdown.md013_line_length import (
    check as _check_md013,
)
from mkforge.verification.rules.markdown.md014_command_prompt import (
    check as _check_md014,
)
from mkforge.verification.rules.markdown.md022_md023_heading_blanks import (
    check as _check_md022_md023,
)
from mkforge.verification.rules.markdown.md026_heading_punctuation import (
    check as _check_md026,
)
from mkforge.verification.rules.markdown.md027_md028_blockquote import (
    check as _check_md027_md028,
)
from mkforge.verification.rules.markdown.md029_md030_list_prefix import (
    check as _check_md029_md030,
)
from mkforge.verification.rules.markdown.md033_inline_html import (
    check as _check_md033,
)
from mkforge.verification.rules.markdown.md035_horizontal_rule import (
    check as _check_md035,
)
from mkforge.verification.rules.markdown.md036_emphasis_heading import (
    check as _check_md036,
)

_check_md005_md006_md007 = _m5.check
_check_md019_md021 = _m19.check
_check_md024_md025 = _m24.check
_check_md031_md032 = _m31.check
_check_md040_md041_md046_md047 = _m40.check
_code_block_style = _m40.code_block_style
_first_line_heading = _m40.first_line_heading

__all__ = [
    "_blank_line_diagnostics",
    "_code_block_style",
    "_code_filtered_lines",
    "_expected_unordered_mark",
    "_first_line_heading",
    "_heading_style_matches",
    "_line_is_too_long",
    "_previous_line_is_list_item",
    "check",
]


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics from all markdownlint-compatible rules.

    Args:
        source: Markdown source context.

    Returns:
        Aggregated diagnostics from every markdownlint rule module.
    """
    checks = (
        _check_md001,
        _check_md002,
        _check_md003,
        _check_md004,
        _check_md005_md006_md007,
        _check_md009,
        _check_md010,
        _check_md012,
        _check_md013,
        _check_md014,
        _check_md019_md021,
        _check_md022_md023,
        _check_md024_md025,
        _check_md026,
        _check_md027_md028,
        _check_md029_md030,
        _check_md031_md032,
        _check_md033,
        _check_md035,
        _check_md036,
        _check_md040_md041_md046_md047,
    )
    return tuple(diagnostic for rule in checks for diagnostic in rule(source))
