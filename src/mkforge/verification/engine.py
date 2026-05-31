"""Markdown verification engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics import (
    Diagnostic,
    RuleConfig,
    RuleRegistry,
    SourceContext,
)
from mkforge.verification.parser import parse_markdown
from mkforge.verification.profiles import GFM_PROFILE
from mkforge.verification.registry import verification_rule_registry


class Verifier:
    """Verifier for Markdown and GitHub Flavored Markdown syntax.

    Attributes:
        profile: Selected verification profile name.
        registry: Registered rules executed by this verifier.
    """

    def __init__(
        self,
        *,
        profile: str = GFM_PROFILE,
        registry: RuleRegistry | None = None,
    ) -> None:
        """Initialize the verifier.

        Args:
            profile: Verification profile name.
            registry: Rule registry to use.
        """
        self.profile = profile
        self.registry = registry or verification_rule_registry(profile)

    def verify(
        self,
        source: str,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Verify one Markdown source string.

        Args:
            source: Markdown source text.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted by enabled verification rules.
        """
        context = parse_markdown(source, config)
        disabled_set = set(disabled or ())
        diagnostics = _run_rules(self.registry, context, disabled_set)
        return tuple(sorted(diagnostics, key=_diagnostic_key))

    def verify_file(
        self,
        path: str | Path,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Verify one UTF-8 Markdown file.

        Args:
            path: UTF-8 Markdown file path.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted for the file.
        """
        source = Path(path).read_text(encoding="utf-8")
        return self.verify(source, config=config, disabled=disabled)


def _diagnostic_key(diagnostic: Diagnostic) -> tuple[int, int, str]:
    """Return the stable diagnostic sort key.

    Args:
        diagnostic: Diagnostic to inspect.

    Returns:
        The stable diagnostic sort key.
    """
    return (diagnostic.line, diagnostic.column, diagnostic.rule_id)


def _run_rules(
    registry: RuleRegistry,
    context: SourceContext,
    disabled: set[str],
) -> list[Diagnostic]:
    """Run enabled rules and collect diagnostics.

    Args:
        registry: Rule registry to use.
        context: Parsed source context and rule configuration.
        disabled: Rule identifiers to skip.

    Returns:
        Run enabled rules and collect diagnostics.
    """
    diagnostics: list[Diagnostic] = []
    for rule in registry.enabled_rules(disabled):
        diagnostics.extend(rule.check(context))
    return diagnostics
