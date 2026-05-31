"""Convenience functions for Markdown verification."""

from collections.abc import Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics import Diagnostic, RuleConfig
from mkforge.verification.engine import Verifier
from mkforge.verification.profiles import GFM_PROFILE


def verify(
    source: str,
    *,
    profile: str = GFM_PROFILE,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: Iterable[str] | None = None,
) -> tuple[Diagnostic, ...]:
    """Verify one Markdown source string.

    Args:
        source: Markdown source text.
        profile: Verification profile name.
        config: Optional per-rule configuration mapping.
        disabled: Rule identifiers to skip.

    Returns:
        Diagnostics emitted by enabled verification rules.
    """
    verifier = Verifier(profile=profile)
    return verifier.verify(source, config=config, disabled=disabled)


def verify_file(
    path: str | Path,
    *,
    profile: str = GFM_PROFILE,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: Iterable[str] | None = None,
) -> tuple[Diagnostic, ...]:
    """Verify one UTF-8 Markdown file.

    Args:
        path: UTF-8 Markdown file path.
        profile: Verification profile name.
        config: Optional per-rule configuration mapping.
        disabled: Rule identifiers to skip.

    Returns:
        Diagnostics emitted for the file.
    """
    verifier = Verifier(profile=profile)
    return verifier.verify_file(path, config=config, disabled=disabled)
