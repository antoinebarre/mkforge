"""Markdown content validation engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics import Diagnostic, RuleConfig, RuleRegistry
from mkforge.diagnostics.engine import DiagnosticEngine
from mkforge.diagnostics.parser import parse_markdown
from mkforge.validation.registry import validation_rule_registry


class Validator:
    """Validator for document-specific Markdown content policies.

    Attributes:
        registry: Registered rules executed by this validator.
    """

    def __init__(self, registry: RuleRegistry | None = None) -> None:
        """Initialize the content validator.

        Args:
            registry: Rule registry to use.
        """
        self.registry = registry or validation_rule_registry()
        self._engine = DiagnosticEngine(self.registry, parse_markdown)

    def validate(
        self,
        source: str,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Validate one Markdown source string.

        Args:
            source: Markdown source text.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted by enabled validation rules.
        """
        return self._engine.run(source, config=config, disabled=disabled)

    def validate_file(
        self,
        path: str | Path,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Validate one UTF-8 Markdown file.

        Args:
            path: UTF-8 Markdown file path.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted for the file.
        """
        return self._engine.run_file(path, config=config, disabled=disabled)


def validate(
    source: str,
    *,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: Iterable[str] | None = None,
) -> tuple[Diagnostic, ...]:
    """Validate one Markdown source string against content rules.

    Args:
        source: Markdown source text.
        config: Optional per-rule configuration mapping.
        disabled: Rule identifiers to skip.

    Returns:
        Diagnostics emitted by enabled validation rules.
    """
    return Validator().validate(source, config=config, disabled=disabled)


def validate_file(
    path: str | Path,
    *,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: Iterable[str] | None = None,
) -> tuple[Diagnostic, ...]:
    """Validate one UTF-8 Markdown file against content rules.

    Args:
        path: UTF-8 Markdown file path.
        config: Optional per-rule configuration mapping.
        disabled: Rule identifiers to skip.

    Returns:
        Diagnostics emitted for the file.
    """
    return Validator().validate_file(path, config=config, disabled=disabled)
