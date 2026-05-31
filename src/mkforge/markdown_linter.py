"""Public Markdown linter entry points."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from mkforge.markdown_lint_parser import parse_markdown
from mkforge.markdown_lint_registry import default_markdown_rule_registry

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mkforge.markdown_lint_api import (
        MarkdownDiagnostic,
        MarkdownRule,
        MarkdownRuleRegistry,
        RuleConfig,
    )


class MarkdownLinter:
    """Configurable Markdown linter."""

    def __init__(self, registry: MarkdownRuleRegistry | None = None) -> None:
        """Initialize a Markdown linter.

        Args:
            registry: Optional rule registry.
        """
        self._registry = registry or default_markdown_rule_registry()

    def register_rule(self, rule: MarkdownRule) -> None:
        """Register a custom rule.

        Args:
            rule: Rule implementation.
        """
        self._registry.register(rule)

    def lint(
        self,
        source: str,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: set[str] | None = None,
    ) -> tuple[MarkdownDiagnostic, ...]:
        """Lint Markdown source text.

        Args:
            source: Markdown source.
            config: Optional per-rule configuration.
            disabled: Optional set of disabled rule identifiers.

        Returns:
            Diagnostics sorted by source location and rule identifier.
        """
        context = parse_markdown(source, config)
        diagnostics: list[MarkdownDiagnostic] = []
        for rule in self._registry.enabled_rules(disabled or set()):
            diagnostics.extend(rule.check(context))
        return tuple(sorted(diagnostics, key=_diagnostic_sort_key))

    def lint_file(
        self,
        path: str | Path,
        *,
        config: Mapping[str, RuleConfig] | None = None,
        disabled: set[str] | None = None,
    ) -> tuple[MarkdownDiagnostic, ...]:
        """Lint a UTF-8 Markdown file.

        Args:
            path: Markdown file path.
            config: Optional per-rule configuration.
            disabled: Optional set of disabled rule identifiers.

        Returns:
            Diagnostics sorted by source location and rule identifier.
        """
        source = Path(path).read_text(encoding="utf-8")
        return self.lint(source, config=config, disabled=disabled)


def lint_markdown(
    source: str,
    *,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: set[str] | None = None,
) -> tuple[MarkdownDiagnostic, ...]:
    """Lint Markdown source using the default linter.

    Args:
        source: Markdown source.
        config: Optional per-rule configuration.
        disabled: Optional set of disabled rule identifiers.

    Returns:
        Diagnostics sorted by source location and rule identifier.
    """
    return MarkdownLinter().lint(source, config=config, disabled=disabled)


def lint_markdown_file(
    path: str | Path,
    *,
    config: Mapping[str, RuleConfig] | None = None,
    disabled: set[str] | None = None,
) -> tuple[MarkdownDiagnostic, ...]:
    """Lint a Markdown file using the default linter.

    Args:
        path: Markdown file path.
        config: Optional per-rule configuration.
        disabled: Optional set of disabled rule identifiers.

    Returns:
        Diagnostics sorted by source location and rule identifier.
    """
    return MarkdownLinter().lint_file(path, config=config, disabled=disabled)


def _diagnostic_sort_key(
    diagnostic: MarkdownDiagnostic,
) -> tuple[int, int, str]:
    """Return deterministic diagnostic sort key."""
    return (diagnostic.line, diagnostic.column, diagnostic.rule_id)
