"""Tests for Markdown content validation."""

from pathlib import Path

from mkforge import (
    Diagnostic,
    FunctionRule,
    RuleRegistry,
    SourceContext,
    Validator,
    validate,
    validate_file,
    verify,
)
from tests.expectations import expect


def test_validation_is_separate_from_verification() -> None:
    """Requirement: content validation rules do not run as verification."""
    source = "# Title?\n\n[here](https://example.com)\n"

    verified = verify(source)
    validated = validate(source)

    expect("MKC003" not in {item.rule_id for item in verified}, verified)
    expect("MKC003" in {item.rule_id for item in validated}, validated)


def test_validation_reports_document_content_diagnostics() -> None:
    """Requirement: validation checks document and content policies."""
    source = (
        "# Title?\n"
        "# Other\n"
        "## Same\n"
        "## Same\n"
        "**Pseudo**\n"
        "```\nx\n```\n"
        "[empty]() and [missing](#absent) and [here](https://e.com)\n"
        "![](ok.png)\n"
        '<img src="x.png">\n'
        "text mkforge\n"
        "[inline](x) and [full][ref]\n"
        "[ref]: x\n"
    )
    config: dict[str, dict[str, object]] = {
        "MKC008": {"headings": ["# Required"]},
        "MKC009": {"names": ["MkForge"]},
        "MKC012": {"inline": False, "full": False},
    }

    diagnostics = validate(source, config=config)
    rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}

    expect("MKC001" in rule_ids, diagnostics)
    expect("MKC005" in rule_ids, diagnostics)
    expect("MKC011" in rule_ids, diagnostics)
    expect("MKC013" in rule_ids, diagnostics)


def test_validation_supports_files_and_disabled_rules(tmp_path: Path) -> None:
    """Requirement: file validation accepts disabled rule identifiers."""
    path = tmp_path / "sample.md"
    path.write_text("# Title?\n", encoding="utf-8")

    diagnostics = validate_file(path, disabled={"MKC003"})

    expect("MKC003" not in {item.rule_id for item in diagnostics}, diagnostics)


def test_validation_supports_custom_public_rules() -> None:
    """Requirement: validators accept public custom diagnostic rules."""

    def check(context: SourceContext) -> tuple[Diagnostic, ...]:
        """Requirement: custom rules receive parsed source context."""
        if "needle" not in context.source:
            return ()
        return (
            Diagnostic(
                "ACME001",
                "Needle",
                1,
                1,
                "Needle is forbidden.",
                "validation",
            ),
        )

    registry = RuleRegistry()
    registry.register(FunctionRule("ACME001", "Needle", check))
    validator = Validator(registry)

    diagnostics = validator.validate("# Title\n\nneedle\n")

    expect(diagnostics[0].rule_id == "ACME001", diagnostics)
