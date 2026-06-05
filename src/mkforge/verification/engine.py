"""Markdown verification engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics import Diagnostic, RuleConfig, RuleRegistry
from mkforge.diagnostics.engine import DiagnosticEngine
from mkforge.diagnostics.parser import parse_markdown
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
        self._engine = DiagnosticEngine(self.registry, parse_markdown)

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
        return self._engine.run(source, config=config, disabled=disabled)

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
        return self._engine.run_file(path, config=config, disabled=disabled)
