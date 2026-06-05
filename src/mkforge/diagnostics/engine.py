"""Shared diagnostic engine used by verification and validation."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

from mkforge.diagnostics.models import Diagnostic, RuleConfig, SourceContext
from mkforge.diagnostics.rules import RuleRegistry

type ParseFn = Callable[[str, Mapping[str, RuleConfig] | None], SourceContext]


class DiagnosticEngine:
    """Rule execution engine shared by Verifier and Validator.

    Attributes:
        registry: Registered rules executed by this engine.
        parse: Callable that parses Markdown source into a SourceContext.
    """

    def __init__(self, registry: RuleRegistry, parse: ParseFn) -> None:
        """Initialize the diagnostic engine.

        Args:
            registry: Rule registry to use.
            parse: Callable that parses a source string into a SourceContext.
        """
        self.registry = registry
        self.parse = parse

    def run(
        self,
        source: str,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Run enabled rules against a Markdown source string.

        Args:
            source: Markdown source text.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted by enabled rules, sorted by position.
        """
        context = self.parse(source, config)
        disabled_set = set(disabled or ())
        diagnostics = _run_rules(self.registry, context, disabled_set)
        return tuple(sorted(diagnostics, key=_diagnostic_key))

    def run_file(
        self,
        path: str | Path,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: Iterable[str] | None = None,
    ) -> tuple[Diagnostic, ...]:
        """Run enabled rules against a UTF-8 Markdown file.

        Args:
            path: UTF-8 Markdown file path.
            config: Optional per-rule configuration mapping.
            disabled: Rule identifiers to skip.

        Returns:
            Diagnostics emitted by enabled rules for the file.
        """
        source = Path(path).read_text(encoding="utf-8")
        return self.run(source, config=config, disabled=disabled)


def _diagnostic_key(diagnostic: Diagnostic) -> tuple[int, int, str]:
    """Return the stable diagnostic sort key.

    Args:
        diagnostic: Diagnostic to inspect.

    Returns:
        Tuple of (line, column, rule_id) used for stable sorting.
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
        Diagnostics collected from all enabled rules.
    """
    diagnostics: list[Diagnostic] = []
    for rule in registry.enabled_rules(disabled):
        diagnostics.extend(rule.check(context))
    return diagnostics
