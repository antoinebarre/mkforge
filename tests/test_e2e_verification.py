"""End-to-end tests for Markdown verification (scenarios 10-16).

These tests exercise the verification public API from the perspective of
a user following the USER_GUIDE.md.  The suite covers:

  - Scenario 10: Verify a Markdown file with local resource check.
  - Scenario 11: Disable rules via VerificationSettings.
  - Scenario 12: Custom conformance rules.
  - Scenario 13: Diagnostics sort order.
  - Scenario 14: TOML settings file override.
  - Scenario 15: MarkdownSource construction.
  - Scenario 16: DownloadAssetError structure.

What-if boundary tests are grouped at the end of each scenario block
and annotated "What-if" in their docstrings.  They verify that the API
fails loudly and predictably at every documented constraint boundary.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from mkforge import (
    Diagnostic,
    DownloadAssetError,
    MarkdownSource,
    VerificationSettings,
    verify_markdown,
    verify_markdown_file,
)

# ---------------------------------------------------------------------------
# Scenario 10 — Verify a Markdown file with local resource check
# ---------------------------------------------------------------------------


def test_e2e_verify_file_reports_missing_local_resource(
    tmp_path: Path,
) -> None:
    """Requirement: verify_markdown_file detects absent local images (MKF001).

    When the user calls verify_markdown_file and an image target does not
    exist relative to the file, MKF001 is emitted with the missing path.
    """
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Title\n\n![Missing](no_such_image.png)\n",
        encoding="utf-8",
    )

    result = verify_markdown_file(
        doc,
        settings=VerificationSettings(disabled=frozenset({"MD013"})),
    )

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MKF001" not in rule_ids:
        raise AssertionError(result.diagnostics)
    if not any("no_such_image.png" in d.message for d in result.diagnostics):
        raise AssertionError(result.diagnostics)


def test_e2e_verify_file_passes_when_local_resource_exists(
    tmp_path: Path,
) -> None:
    """Requirement: verify_markdown_file omits MKF001 for existing images.

    The happy path: the image file is present alongside the Markdown file.
    No MKF001 diagnostic should be emitted.
    """
    image = tmp_path / "logo.png"
    image.write_bytes(b"\x89PNG")
    doc = tmp_path / "doc.md"
    doc.write_text("# Title\n\n![Logo](logo.png)\n", encoding="utf-8")

    result = verify_markdown_file(
        doc,
        settings=VerificationSettings(disabled=frozenset({"MD013"})),
    )

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MKF001" in rule_ids:
        raise AssertionError(result.diagnostics)


def test_e2e_verify_file_ignores_remote_urls_for_mkf001(
    tmp_path: Path,
) -> None:
    """Requirement: MKF001 does not check remote image URLs.

    Remote image references are not verified for local existence since
    they cannot be resolved as filesystem paths.
    """
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Title\n\n![Remote](https://example.com/img.png)\n",
        encoding="utf-8",
    )

    result = verify_markdown_file(
        doc,
        settings=VerificationSettings(disabled=frozenset({"MD013"})),
    )

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MKF001" in rule_ids:
        raise AssertionError(result.diagnostics)


def test_e2e_verify_raw_text_without_path_skips_mkf001() -> None:
    """Requirement: verify_markdown without source_path skips MKF001.

    When no file path is given, MKF001 cannot resolve relative references
    and must be silently skipped to avoid false positives.
    """
    source = "![Missing](does_not_exist.png)\n"
    result = verify_markdown(
        source,
        settings=VerificationSettings(disabled=frozenset({"MD041"})),
    )

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MKF001" in rule_ids:
        raise AssertionError(result.diagnostics)


# ---------------------------------------------------------------------------
# Scenario 11 — Disable rules via VerificationSettings
# ---------------------------------------------------------------------------


def test_e2e_disable_single_rule_removes_its_diagnostics() -> None:
    """Requirement: a disabled rule_id produces no diagnostics.

    A rule listed in VerificationSettings.disabled must not appear in
    the resulting diagnostics tuple.
    """
    source = "#NoSpace\n"
    result_default = verify_markdown(source)
    result_disabled = verify_markdown(
        source,
        settings=VerificationSettings(disabled=frozenset({"MD018"})),
    )

    if "MD018" not in {d.rule_id for d in result_default.diagnostics}:
        raise AssertionError(result_default.diagnostics)
    if "MD018" in {d.rule_id for d in result_disabled.diagnostics}:
        raise AssertionError(result_disabled.diagnostics)


def test_e2e_disable_multiple_rules_removes_all_of_them() -> None:
    """Requirement: multiple disabled rule IDs are all suppressed.

    Disabling a set of rules must remove all of them from diagnostics
    without affecting other rules.
    """
    source = "# Title\n\nSee http://example.com\n"
    settings = VerificationSettings(
        disabled=frozenset({"MD034", "MD013"}),
    )
    result = verify_markdown(source, settings=settings)

    ids = {d.rule_id for d in result.diagnostics}
    for rule_id in ("MD034", "MD013"):
        if rule_id in ids:
            msg = f"{rule_id} found despite being disabled"
            raise AssertionError(msg)


def test_e2e_wif_disable_requires_uppercase_rule_ids() -> None:
    """Requirement: programmatic disabled frozenset uses uppercase rule IDs.

    What-if: a caller passes lowercase rule IDs in the frozenset.
    VerificationSettings does not normalise programmatic input, so
    lowercase IDs do NOT suppress rules.  Only TOML loading normalises.
    The user guide documents that rule IDs must be uppercase when passed
    programmatically.
    """
    source = "#NoSpace\n"
    settings_lower = VerificationSettings(disabled=frozenset({"md018"}))
    result = verify_markdown(source, settings=settings_lower)

    ids = {d.rule_id for d in result.diagnostics}
    if "MD018" not in ids:
        raise AssertionError(ids)


# ---------------------------------------------------------------------------
# Scenario 12 — Custom conformance rules
# ---------------------------------------------------------------------------


def _require_footer(
    source: MarkdownSource,
) -> tuple[Diagnostic, ...]:
    """Return a diagnostic when the source has no HTML footer comment.

    Args:
        source: Markdown source context.

    Returns:
        Tuple with one diagnostic if the footer is absent, else empty.
    """
    if "<!-- footer -->" not in source.text:
        return (
            Diagnostic(
                rule_id="ACME001",
                name="missing-footer",
                line=len(source.lines),
                column=1,
                message="Document must end with <!-- footer -->.",
            ),
        )
    return ()


def test_e2e_custom_rule_fires_on_matching_source() -> None:
    """Requirement: a custom rule callable is invoked and its diagnostic fires.

    The user guide shows how to write a MarkdownRule callable and pass it
    via custom_rules.  The resulting diagnostic must appear in the report.
    """
    source = "# Title\n\nContent without footer.\n"
    result = verify_markdown(source, custom_rules=(_require_footer,))

    ids = {d.rule_id for d in result.diagnostics}
    if "ACME001" not in ids:
        raise AssertionError(result.diagnostics)


def test_e2e_custom_rule_receives_full_source_context() -> None:
    """Requirement: MarkdownSource passed to a custom rule has text and lines.

    A custom rule that inspects individual lines must receive a complete
    MarkdownSource context with one-based line numbers.
    """
    received: list[MarkdownSource] = []

    def capture(source: MarkdownSource) -> tuple[Diagnostic, ...]:
        """Capture the source context for the test assertion.

        Args:
            source: Markdown source context to capture.

        Returns:
            Empty diagnostic tuple.
        """
        received.append(source)
        return ()

    source_text = "# Hello\n\nParagraph.\n"
    verify_markdown(source_text, custom_rules=(capture,))

    if not received:
        raise AssertionError(received)
    ctx = received[0]
    if ctx.text != source_text:
        raise AssertionError(ctx.text)
    if len(ctx.lines) != 3:  # noqa: PLR2004
        raise AssertionError(ctx.lines)
    if ctx.lines[0].number != 1:
        raise AssertionError(ctx.lines[0])
    if ctx.lines[0].text != "# Hello":
        raise AssertionError(ctx.lines[0])


def test_e2e_custom_rule_can_be_disabled_by_settings() -> None:
    """Requirement: custom rule IDs participate in the disabled filter.

    A custom rule whose rule_id is in VerificationSettings.disabled must
    not appear in the resulting diagnostics.
    """

    def always_fires(_source: MarkdownSource) -> tuple[Diagnostic, ...]:
        """Always emit one diagnostic for disable-filter testing.

        Args:
            _source: Markdown source context (unused).

        Returns:
            Tuple containing one always-active diagnostic.
        """
        return (
            Diagnostic(
                rule_id="CUSTOM001",
                name="always",
                line=1,
                column=1,
                message="Always fires.",
            ),
        )

    settings = VerificationSettings(disabled=frozenset({"CUSTOM001"}))
    result = verify_markdown(
        "# Title\n",
        settings=settings,
        custom_rules=(always_fires,),
    )

    ids = {d.rule_id for d in result.diagnostics}
    if "CUSTOM001" in ids:
        raise AssertionError(ids)


# ---------------------------------------------------------------------------
# Scenario 13 — Diagnostics sort order
# ---------------------------------------------------------------------------


def test_e2e_diagnostics_sorted_by_line_then_column_then_rule_id() -> None:
    """Requirement: diagnostics are sorted by (line, column, rule_id).

    A user who iterates diagnostics must see them in stable document order
    regardless of rule execution order.
    """
    source = "#NoSpace\n# Heading#\n"
    result = verify_markdown(source)

    keys = [(d.line, d.column, d.rule_id) for d in result.diagnostics]
    if keys != sorted(keys):
        raise AssertionError(result.diagnostics)


def test_e2e_diagnostic_fields_have_expected_defaults() -> None:
    """Requirement: Diagnostic defaults category and severity correctly.

    The user guide documents category='markdown-conformance' and
    severity='warning' as the defaults for programmatically constructed
    Diagnostic objects.
    """
    d = Diagnostic(
        rule_id="TEST001",
        name="test-rule",
        line=1,
        column=1,
        message="Test.",
    )
    if d.category != "markdown-conformance":
        raise AssertionError(d.category)
    if d.severity != "warning":
        raise AssertionError(d.severity)


# ---------------------------------------------------------------------------
# Scenario 14 — TOML settings file override
# ---------------------------------------------------------------------------


def test_e2e_toml_settings_disables_and_overrides_options(
    tmp_path: Path,
) -> None:
    """Requirement: .mkforge TOML file overrides options and disables rules.

    A user who places a .mkforge file next to their Markdown can configure
    mkforge without passing VerificationSettings objects explicitly.
    verify_markdown_file must discover and apply the settings automatically.
    """
    settings_file = tmp_path / ".mkforge"
    settings_file.write_text(
        textwrap.dedent("""\
            [verification]
            disabled = ["MD034"]

            [verification.rules.MD013]
            line_length = 200
        """),
        encoding="utf-8",
    )
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Title\n\nSee http://example.com — long line in the text.\n",
        encoding="utf-8",
    )

    result = verify_markdown_file(doc)

    ids = {d.rule_id for d in result.diagnostics}
    if "MD034" in ids:
        raise AssertionError(ids)
    if "MD013" in ids:
        raise AssertionError(ids)


def test_e2e_toml_pyproject_verification_section_is_discovered(
    tmp_path: Path,
) -> None:
    """Requirement: [tool.mkforge.verification] in pyproject.toml is loaded.

    The user guide documents pyproject.toml as an alternative settings
    source discovered automatically by verify_markdown_file.
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        textwrap.dedent("""\
            [tool.mkforge.verification]
            disabled = ["MD041"]
        """),
        encoding="utf-8",
    )
    doc = tmp_path / "doc.md"
    doc.write_text("Paragraph without heading.\n", encoding="utf-8")

    result = verify_markdown_file(doc)

    ids = {d.rule_id for d in result.diagnostics}
    if "MD041" in ids:
        raise AssertionError(ids)


def test_e2e_toml_settings_normalise_rule_ids_to_uppercase(
    tmp_path: Path,
) -> None:
    """Requirement: TOML settings normalise disabled rule IDs to uppercase.

    Unlike programmatic VerificationSettings, the TOML loader calls
    _string_list which calls .upper().  Lowercase rule IDs in TOML must
    suppress the rule just as uppercase IDs do.
    """
    settings_file = tmp_path / ".mkforge"
    settings_file.write_text(
        '[verification]\ndisabled = ["md041"]\n',
        encoding="utf-8",
    )
    doc = tmp_path / "doc.md"
    doc.write_text("Paragraph without heading.\n", encoding="utf-8")

    result = verify_markdown_file(doc)

    ids = {d.rule_id for d in result.diagnostics}
    if "MD041" in ids:
        raise AssertionError(ids)


# ---------------------------------------------------------------------------
# Scenario 15 — MarkdownSource construction
# ---------------------------------------------------------------------------

_LINE_TWO = 2
_LINE_THREE = 3


def test_e2e_markdown_source_from_text_numbers_lines_from_one() -> None:
    """Requirement: MarkdownSource.from_text produces one-based line numbers.

    Custom rule authors rely on one-based numbering to report accurate
    line positions in Diagnostic objects.
    """
    source = MarkdownSource.from_text("line one\nline two\nline three\n")

    if source.lines[0].number != 1:
        raise AssertionError(source.lines[0])
    if source.lines[0].text != "line one":
        raise AssertionError(source.lines[0])
    if source.lines[1].number != _LINE_TWO:
        raise AssertionError(source.lines[1])
    if source.lines[2].number != _LINE_THREE:
        raise AssertionError(source.lines[2])


def test_e2e_markdown_source_records_path(tmp_path: Path) -> None:
    """Requirement: MarkdownSource.from_text records source_path as a Path.

    Custom rules that check local resource targets use source.path to
    resolve relative references.
    """
    doc = tmp_path / "doc.md"
    source = MarkdownSource.from_text("# Title\n", source_path=doc)

    if source.path != doc:
        raise AssertionError(source.path)


def test_e2e_markdown_source_without_path_has_none_path() -> None:
    """Requirement: MarkdownSource.from_text sets path=None with no path arg.

    Rules that require a path must check source.path is not None before
    attempting file system access to avoid false positives.
    """
    source = MarkdownSource.from_text("# Title\n")
    if source.path is not None:
        raise AssertionError(source.path)


# ---------------------------------------------------------------------------
# Scenario 16 — DownloadAssetError structure
# ---------------------------------------------------------------------------


def test_e2e_download_asset_error_exposes_url_and_reason() -> None:
    """Requirement: DownloadAssetError exposes url and reason attributes.

    A CI wrapper that catches DownloadAssetError must be able to log the
    URL and reason independently without parsing the exception message.
    """
    err = DownloadAssetError("https://example.com/img.png", "timeout")
    if err.url != "https://example.com/img.png":
        raise AssertionError(err.url)
    if err.reason != "timeout":
        raise AssertionError(err.reason)
    if "https://example.com/img.png" not in str(err):
        raise AssertionError(str(err))
    if "timeout" not in str(err):
        raise AssertionError(str(err))


def test_e2e_wif_download_asset_error_is_mkforge_error() -> None:
    """Requirement: DownloadAssetError is a subclass of MkForgeError.

    What-if: a caller catches the base MkForgeError.  DownloadAssetError
    must be catchable via the base class as documented in the error table.
    """
    from mkforge.errors import MkForgeError  # noqa: PLC0415

    err = DownloadAssetError("https://example.com/img.png", "refused")
    if not isinstance(err, MkForgeError):
        raise TypeError(type(err))


def test_e2e_wif_missing_asset_error_is_mkforge_error() -> None:
    """Requirement: MissingAssetError is a subclass of MkForgeError.

    What-if: a caller catches the base MkForgeError.  MissingAssetError
    must be catchable via the base class as documented in the error table.
    """
    from mkforge.errors import MissingAssetError, MkForgeError  # noqa: PLC0415

    err = MissingAssetError([Path("/a/b.png")])
    if not isinstance(err, MkForgeError):
        raise TypeError(type(err))
