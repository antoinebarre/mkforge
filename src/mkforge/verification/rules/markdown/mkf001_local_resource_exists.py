"""MD003 checks that local Markdown resources resolve from the source file.

This rule belongs to Markdown verification because local link and image targets
are source-level resource references. It emits one diagnostic when a relative
resource target cannot be found from the Markdown file directory.
"""

from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

from mkforge.verification.policy import Diagnostic, MarkdownSource

RULE_ID = "MKF001"
NAME = "Local resource exists"
RESOURCE_TARGET = re.compile(r"!?\[[^\]]*]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check(source: MarkdownSource) -> tuple[Diagnostic, ...]:
    """Return diagnostics for missing local image or link targets.

    Args:
        source: Markdown source context.

    Returns:
        Diagnostics for missing local resources.
    """
    if source.path is None:
        return ()
    diagnostics: list[Diagnostic] = []
    for line in source.lines:
        for match in RESOURCE_TARGET.finditer(line.text):
            target = _resource_target(match.group(1))
            if _is_missing_local_target(source, target):
                diagnostics.append(
                    _diagnostic(line.number, match.start(1), target),
                )
    return tuple(diagnostics)


def _resource_target(raw_target: str) -> str:
    """Return the normalized target part before any fragment.

    Args:
        raw_target: Raw Markdown resource target.

    Returns:
        Unquoted resource path without a fragment suffix.
    """
    return unquote(raw_target.split("#", maxsplit=1)[0].strip())


def _is_missing_local_target(source: MarkdownSource, target: str) -> bool:
    """Return whether a local target should exist but does not.

    Args:
        source: Markdown source context with a path.
        target: Resource target path.

    Returns:
        True when the target is local and absent.
    """
    if not target or not _is_local_file_target(target):
        return False
    if source.path is None:
        return False
    return not (source.path.parent / target).exists()


def _is_local_file_target(target: str) -> bool:
    """Return whether a Markdown target refers to a local file.

    Args:
        target: Normalized resource target.

    Returns:
        True when the target has no URL scheme and is not fragment-only.
    """
    parsed = urlparse(target)
    return not parsed.scheme and not target.startswith("#")


def _diagnostic(line: int, zero_based_column: int, target: str) -> Diagnostic:
    """Return a missing-resource diagnostic.

    Args:
        line: One-based line number.
        zero_based_column: Zero-based column where the target starts.
        target: Missing local target.

    Returns:
        Missing-resource diagnostic.
    """
    return Diagnostic(
        rule_id=RULE_ID,
        name=NAME,
        line=line,
        column=zero_based_column + 1,
        message=f"Referenced local resource does not exist: {target}",
    )
