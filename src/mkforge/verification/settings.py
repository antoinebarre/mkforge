"""TOML settings for Markdown verification rules."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RuleOptions = dict[str, object]


@dataclass(frozen=True)
class VerificationSettings:
    """Settings applied to Markdown verification.

    Attributes:
        disabled: Rule identifiers skipped by verification.
        rules: Per-rule option mappings.
    """

    disabled: frozenset[str] = frozenset()
    rules: dict[str, RuleOptions] = field(default_factory=dict)

    def rule_options(self, rule_id: str) -> RuleOptions:
        """Return options for one rule.

        Args:
            rule_id: Rule identifier to read.

        Returns:
            Rule option mapping.
        """
        return dict(self.rules.get(rule_id, {}))


def default_settings() -> VerificationSettings:
    """Return markdownlint-compatible default settings.

    Returns:
        Verification settings with default rule parameters.
    """
    return VerificationSettings(rules=_default_rule_options())


def load_settings(start: str | Path | None = None) -> VerificationSettings:
    """Load verification settings from .mkforge or pyproject.toml.

    Args:
        start: Directory or file path used to find settings.

    Returns:
        Loaded settings merged over markdownlint-compatible defaults.
    """
    root = _settings_root(start)
    settings = default_settings()
    for path in _settings_files(root):
        settings = _merge_settings(settings, _read_settings(path))
    return settings


def _settings_root(start: str | Path | None) -> Path:
    """Return the directory used to discover settings.

    Args:
        start: Optional file or directory path.

    Returns:
        Settings discovery directory.
    """
    if start is None:
        return Path.cwd()
    path = Path(start)
    if path.suffix or path.is_file():
        return path.parent
    return path


def _settings_files(root: Path) -> tuple[Path, ...]:
    """Return settings files from nearest project root.

    Args:
        root: Directory where discovery starts.

    Returns:
        Existing settings files in load order.
    """
    for directory in (root.resolve(), *root.resolve().parents):
        candidates = (
            directory / "pyproject.toml",
            directory / ".mkforge.toml",
            directory / ".mkforge",
        )
        found = tuple(path for path in candidates if path.exists())
        if found:
            return found
    return ()


def _read_settings(path: Path) -> VerificationSettings:
    """Read one TOML settings file.

    Args:
        path: TOML settings file.

    Returns:
        Verification settings declared by the file.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    table = _verification_table(data, path)
    disabled = frozenset(_string_list(table.get("disabled", ())))
    rules = {
        rule_id.upper(): dict(options)
        for rule_id, options in table.get("rules", {}).items()
        if isinstance(options, dict)
    }
    return VerificationSettings(disabled=disabled, rules=rules)


def _verification_table(data: dict[str, Any], path: Path) -> dict[str, Any]:
    """Return the verification settings table.

    Args:
        data: Parsed TOML data.
        path: Settings file path.

    Returns:
        Verification settings table.
    """
    if path.name == "pyproject.toml":
        tool = data.get("tool", {})
        if not isinstance(tool, dict):
            return {}
        mkforge = tool.get("mkforge", {})
        if not isinstance(mkforge, dict):
            return {}
        table = mkforge.get("verification", {})
        return table if isinstance(table, dict) else {}
    table = data.get("verification", data)
    return table if isinstance(table, dict) else {}


def _string_list(value: object) -> tuple[str, ...]:
    """Return upper-case strings from a TOML list value.

    Args:
        value: Candidate TOML list.

    Returns:
        Upper-case string tuple.
    """
    if not isinstance(value, list | tuple):
        return ()
    return tuple(item.upper() for item in value if isinstance(item, str))


def _merge_settings(
    base: VerificationSettings,
    override: VerificationSettings,
) -> VerificationSettings:
    """Merge settings with override values.

    Args:
        base: Base settings.
        override: User-supplied settings.

    Returns:
        Merged settings.
    """
    rules = {key: dict(value) for key, value in base.rules.items()}
    for rule_id, options in override.rules.items():
        existing = rules.get(rule_id, {})
        rules[rule_id] = {**existing, **options}
    return VerificationSettings(
        disabled=base.disabled | override.disabled,
        rules=rules,
    )


def _default_rule_options() -> dict[str, RuleOptions]:
    """Return markdownlint-compatible default rule options.

    Returns:
        Default options by rule identifier.
    """
    return {
        "MD001": {"front_matter_title": r"^\s*title\s*[:=]"},
        "MD002": {"level": 1, "front_matter_title": r"^\s*title\s*[:=]"},
        "MD003": {"style": "consistent"},
        "MD004": {"style": "consistent"},
        "MD007": {"indent": 3},
        "MD009": {"br_spaces": 2},
        "MD010": {"ignore_code_blocks": False},
        "MD013": {
            "line_length": 80,
            "ignore_code_blocks": False,
            "code_blocks": True,
            "tables": True,
            "headings": True,
            "treat_links_as_single_words": False,
        },
        "MD024": {"allow_different_nesting": False},
        "MD025": {"level": 1, "front_matter_title": r"^\s*title\s*[:=]"},
        "MD026": {"punctuation": ".,;:!?"},
        "MD029": {"style": "one"},
        "MD030": {
            "ul_single": 1,
            "ol_single": 1,
            "ul_multi": 1,
            "ol_multi": 1,
        },
        "MD033": {"allowed_elements": ""},
        "MD035": {"style": "consistent"},
        "MD036": {"punctuation": ".,;:!?"},
        "MD041": {"level": 1, "front_matter_title": r"^\s*title\s*[:=]"},
        "MD046": {"style": "fenced"},
    }
