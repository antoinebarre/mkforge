"""Public Markdown conformance verification API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from mkforge.verification.policy import (
    Diagnostic,
    MarkdownRule,
    MarkdownSource,
)
from mkforge.verification.registry import MARKDOWN_COMPLIANCE
from mkforge.verification.settings import VerificationSettings, load_settings


@dataclass(frozen=True)
class VerificationReport:
    """Structured result returned by Markdown verification.

    Attributes:
        rule_set_name: Name of the built-in rule set used for verification.
        diagnostics: Sorted conformance diagnostics.
    """

    rule_set_name: str
    diagnostics: tuple[Diagnostic, ...]

    @property
    def passed(self) -> bool:
        """Return whether no conformance diagnostics were emitted.

        Returns:
            True when the report contains no diagnostics.
        """
        return not self.diagnostics

    @property
    def has_errors(self) -> bool:
        """Return whether any diagnostic has error severity.

        Returns:
            True when at least one diagnostic is an error.
        """
        return any(item.severity == "error" for item in self.diagnostics)

    @property
    def has_warnings(self) -> bool:
        """Return whether any diagnostic has warning severity.

        Returns:
            True when at least one diagnostic is a warning.
        """
        return any(item.severity == "warning" for item in self.diagnostics)


def verify_markdown(
    source: str,
    *,
    source_path: str | Path | None = None,
    settings: VerificationSettings | None = None,
    custom_rules: Iterable[MarkdownRule] = (),
) -> VerificationReport:
    """Verify Markdown source against the built-in conformance rules.

    Args:
        source: Markdown source text.
        source_path: Optional path used to resolve local resources.
        settings: Optional settings overriding TOML discovery.
        custom_rules: One-call conformance rules appended after built-in rules.

    Returns:
        Verification report containing sorted diagnostics.
    """
    active_settings = settings or load_settings(source_path)
    markdown_source = MarkdownSource.from_text(
        source,
        source_path=source_path,
        settings=active_settings,
    )
    rules = (*MARKDOWN_COMPLIANCE.rules, *tuple(custom_rules))
    diagnostics = _enabled_diagnostics(
        markdown_source,
        tuple(
            diagnostic
            for rule in rules
            for diagnostic in rule(markdown_source)
        ),
    )
    return VerificationReport(
        rule_set_name=MARKDOWN_COMPLIANCE.name,
        diagnostics=tuple(sorted(diagnostics, key=_diagnostic_key)),
    )


def verify_markdown_file(
    path: str | Path,
    *,
    settings: VerificationSettings | None = None,
    custom_rules: Iterable[MarkdownRule] = (),
) -> VerificationReport:
    """Verify one UTF-8 Markdown file against built-in conformance rules.

    Args:
        path: Markdown file path.
        settings: Optional settings overriding TOML discovery.
        custom_rules: One-call conformance rules appended after built-in rules.

    Returns:
        Verification report containing sorted diagnostics.
    """
    markdown_path = Path(path)
    return verify_markdown(
        markdown_path.read_text(encoding="utf-8"),
        source_path=markdown_path,
        settings=settings,
        custom_rules=custom_rules,
    )


def _enabled_diagnostics(
    source: MarkdownSource,
    diagnostics: tuple[Diagnostic, ...],
) -> tuple[Diagnostic, ...]:
    """Return diagnostics whose rules are enabled.

    Args:
        source: Markdown source context.
        diagnostics: Diagnostics emitted by rules.

    Returns:
        Diagnostics not disabled in settings.
    """
    disabled = source.settings.disabled
    return tuple(
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.rule_id.upper() not in disabled
    )


def _diagnostic_key(diagnostic: Diagnostic) -> tuple[int, int, str]:
    """Return the stable diagnostic sort key.

    Args:
        diagnostic: Diagnostic to sort.

    Returns:
        Tuple sorting by line, column, then rule identifier.
    """
    return (diagnostic.line, diagnostic.column, diagnostic.rule_id)
