"""Markdown content validation engine."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics import (
    Diagnostic,
    RuleConfig,
    RuleRegistry,
    SourceContext,
)
from mkforge.validation.registry import validation_rule_registry
from mkforge.verification.parser import parse_markdown


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
        context = parse_markdown(source, config)
        disabled_set = set(disabled or ())
        diagnostics = _run_rules(self.registry, context, disabled_set)
        return tuple(sorted(diagnostics, key=_diagnostic_key))

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
        source = Path(path).read_text(encoding="utf-8")
        return self.validate(source, config=config, disabled=disabled)


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
    validator = Validator()
    return validator.validate(source, config=config, disabled=disabled)


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
    validator = Validator()
    return validator.validate_file(path, config=config, disabled=disabled)
