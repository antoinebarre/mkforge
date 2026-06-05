"""Tests for the shared DiagnosticEngine."""

from pathlib import Path

from mkforge.diagnostics.engine import DiagnosticEngine
from mkforge.diagnostics.models import Diagnostic, SourceContext
from mkforge.diagnostics.parser import parse_markdown
from mkforge.diagnostics.rules import FunctionRule, RuleRegistry
from tests.expectations import expect


def _fixed_diagnostic(rule_id: str, line: int) -> Diagnostic:
    """Return a diagnostic at the given line number.

    Args:
        rule_id: Rule identifier to use.
        line: One-based line number.

    Returns:
        Diagnostic with the given rule identifier and line number.
    """
    return Diagnostic(rule_id, "Name", line, 1, "msg", "test")


def _rule_emitting(rule_id: str, line: int) -> FunctionRule:
    """Build a rule that always emits one diagnostic at a fixed line.

    Args:
        rule_id: Rule identifier to use.
        line: One-based line number for the emitted diagnostic.

    Returns:
        FunctionRule that emits one diagnostic.
    """

    def check(_: SourceContext) -> tuple[Diagnostic, ...]:
        """Return one fixed diagnostic.

        Args:
            _: Parsed source context (unused).

        Returns:
            Tuple containing one diagnostic.
        """
        return (_fixed_diagnostic(rule_id, line),)

    return FunctionRule(rule_id, "Name", check)


def _engine_with(*rules: FunctionRule) -> DiagnosticEngine:
    """Build a DiagnosticEngine from a sequence of rules.

    Args:
        *rules: FunctionRule instances to register.

    Returns:
        DiagnosticEngine with the given rules registered.
    """
    registry = RuleRegistry()
    for rule in rules:
        registry.register(rule)
    return DiagnosticEngine(registry, parse_markdown)


def test_engine_returns_empty_tuple_for_empty_registry() -> None:
    """Requirement: an engine with no rules emits no diagnostics."""
    engine = DiagnosticEngine(RuleRegistry(), parse_markdown)
    expect(engine.run("# Title\n") == (), None)


def test_engine_collects_diagnostics_from_rule() -> None:
    """Requirement: the engine collects diagnostics emitted by rules."""
    result = _engine_with(_rule_emitting("T001", 1)).run("# Title\n")
    expect(len(result) == 1, result)
    expect(result[0].rule_id == "T001", result)


def test_engine_sorts_diagnostics_by_position() -> None:
    """Requirement: diagnostics are sorted by line, column, rule_id."""
    engine = _engine_with(_rule_emitting("T002", 3), _rule_emitting("T001", 1))
    result = engine.run("# Title\n\nParagraph\n")
    expect(result[0].rule_id == "T001", result)
    expect(result[1].rule_id == "T002", result)


def test_engine_skips_disabled_rules() -> None:
    """Requirement: the engine skips rules listed in the disabled set."""
    engine = _engine_with(_rule_emitting("T001", 1), _rule_emitting("T002", 1))
    result = engine.run("# Title\n", disabled={"T001"})
    rule_ids = {d.rule_id for d in result}
    expect("T001" not in rule_ids, result)
    expect("T002" in rule_ids, result)


def test_engine_disabled_none_disables_nothing() -> None:
    """Requirement: passing disabled=None disables nothing."""
    result = _engine_with(_rule_emitting("T001", 1)).run(
        "# Title\n",
        disabled=None,
    )
    expect(len(result) == 1, result)


def test_engine_run_file_reads_utf8_file(tmp_path: Path) -> None:
    """Requirement: run_file reads a UTF-8 file and delegates to run."""
    md_file = tmp_path / "doc.md"
    md_file.write_text("# Title\n", encoding="utf-8")
    result = _engine_with(_rule_emitting("T001", 1)).run_file(md_file)
    expect(len(result) == 1, result)
    expect(result[0].rule_id == "T001", result)


def test_engine_run_file_accepts_string_path(tmp_path: Path) -> None:
    """Requirement: run_file accepts a string path in addition to Path."""
    md_file = tmp_path / "doc.md"
    md_file.write_text("# Title\n", encoding="utf-8")
    result = _engine_with(_rule_emitting("T001", 1)).run_file(str(md_file))
    expect(len(result) == 1, result)


def test_engine_passes_config_to_context() -> None:
    """Requirement: config is forwarded to the parsed SourceContext."""

    def check_config(context: SourceContext) -> tuple[Diagnostic, ...]:
        """Emit a diagnostic when the expected config flag is present.

        Args:
            context: Parsed source context.

        Returns:
            One diagnostic when config flag is set, empty tuple otherwise.
        """
        if context.rule_config("T_CFG").get("flag") == "yes":
            return (_fixed_diagnostic("T_CFG", 1),)
        return ()

    registry = RuleRegistry()
    registry.register(FunctionRule("T_CFG", "Cfg", check_config))
    engine = DiagnosticEngine(registry, parse_markdown)
    expect(len(engine.run("# Title\n")) == 0, None)
    with_cfg = engine.run("# Title\n", config={"T_CFG": {"flag": "yes"}})
    expect(len(with_cfg) == 1, with_cfg)
