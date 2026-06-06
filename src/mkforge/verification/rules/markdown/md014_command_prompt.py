"""MD014 checks for unnecessary shell prompt markers in code blocks.

This rule belongs to Markdown verification because shell prompts (``$ ``)
inside fenced blocks that contain only commands prevent copy-paste reuse.
It emits one diagnostic per command line in a block where every line starts
with a prompt marker.
"""

from __future__ import annotations

from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.rules.markdown._shared import (
    _diagnostic,
    _fenced_blocks,
)


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for shell prompt markers in command-only code blocks.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for each command line with an unnecessary prompt marker.
    """
    diagnostics: list[Diagnostic] = []
    for block in _fenced_blocks(source):
        command_lines = [
            line for line in block.lines if line.text.startswith("$ ")
        ]
        if command_lines and len(command_lines) == len(block.lines):
            diagnostics.extend(
                _diagnostic(
                    "MD014",
                    line.number,
                    1,
                    "Remove unnecessary shell prompt markers.",
                )
                for line in command_lines
            )
    return tuple(diagnostics)
