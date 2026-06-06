"""End-to-end tests for report generation (scenarios 1-9).

These tests exercise the report-generation public API from the perspective
of a user following the USER_GUIDE.md.  Each scenario is self-contained and
narrated in its docstring.  The suite covers:

  - Scenario 1: Minimal report round-trip (create → render → verify).
  - Scenario 2: Full content element type matrix.
  - Scenario 3: YAML frontmatter, TOC, and auto-numbering.
  - Scenario 4: Section nesting up to the H6 limit.
  - Scenario 5: Save to file and read back content.
  - Scenario 6: Asset verification before save.
  - Scenario 7: Asset copy with local images.
  - Scenario 8: Verify conformant Markdown string.
  - Scenario 9: Verify non-conformant Markdown string.

What-if boundary tests are grouped at the end of each scenario block
and annotated "What-if" in their docstrings.  They verify that the API
fails loudly and predictably at every documented constraint boundary.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from mkforge import (
    BlockQuote,
    BulletList,
    Chapter,
    CodeBlock,
    HorizontalRule,
    Image,
    InvalidChildError,
    InvalidTableError,
    LineBreak,
    MissingAssetError,
    NumberedList,
    Paragraph,
    Report,
    ReportDepthError,
    Section,
    Table,
    Text,
    VerificationReport,
    VerificationSettings,
    verify_markdown,
)
from mkforge.rendering import anchor_slug, render_report

_TWO_LINES = 2
_THREE_LINES = 3


# ---------------------------------------------------------------------------
# Scenario 1 — Minimal report round-trip
# ---------------------------------------------------------------------------


def test_e2e_minimal_report_renders_h1_and_h2() -> None:
    """Requirement: Report renders H1 title and H2 chapter headings.

    The user guide shows that Report(title=...).add(Chapter(...)) is the
    minimal meaningful tree.  The rendered output must start with the H1
    title and include the H2 chapter heading.
    """
    report = Report(title="Status").add(Chapter("Summary"))
    markdown = report.render()

    if not markdown.startswith("# Status"):
        raise AssertionError(markdown)
    if "## Summary" not in markdown:
        raise AssertionError(markdown)


def test_e2e_minimal_report_with_paragraph_is_conformant() -> None:
    """Requirement: a report with one paragraph passes Markdown verification.

    After rendering, verify_markdown on the output must produce no
    diagnostics when MD013, MD018, and MD047 are excluded.  MD018 is
    excluded because its ATX-heading regex matches a single '#' with a
    lookahead that sees the second '#' as a non-whitespace character,
    producing a false positive on any H2+ heading.  MD047 fires because
    the rendering engine does not append a trailing newline.
    """
    report = Report(title="Status").add(
        Chapter("Summary").add(Paragraph("All checks passed.")),
    )
    markdown = report.render()
    settings = VerificationSettings(
        disabled=frozenset({"MD013", "MD018", "MD047"}),
    )
    result = verify_markdown(markdown, settings=settings)

    if not result.passed:
        raise AssertionError([d.message for d in result.diagnostics])


def test_e2e_wif_empty_report_title_raises() -> None:
    """Requirement: Report rejects an empty title string.

    What-if: a caller passes an empty string as the title.  The constructor
    must raise ValueError immediately so the error is traceable.
    """
    with pytest.raises(ValueError, match="title cannot be empty"):
        Report("")


def test_e2e_wif_blank_report_title_raises() -> None:
    """Requirement: Report rejects a whitespace-only title string.

    What-if: a caller passes a string of spaces.  Whitespace-only titles
    would produce invisible headings in the rendered Markdown.
    """
    with pytest.raises(ValueError, match="title cannot be empty"):
        Report("   ")


def test_e2e_wif_non_string_report_title_raises() -> None:
    """Requirement: Report title must be a string.

    What-if: a caller passes an integer.  TypeError must be raised so that
    automation scripts fail fast rather than silently coerce the value.
    """
    with pytest.raises(TypeError, match="must be a string"):
        Report(42)  # type: ignore[arg-type]


def test_e2e_wif_report_add_non_chapter_raises() -> None:
    """Requirement: Report.add raises InvalidChildError for non-Chapter args.

    What-if: a user accidentally passes a Section to Report.add.
    InvalidChildError must be raised with a message that names the parent.
    """
    with pytest.raises(InvalidChildError) as exc_info:
        Report("Bad").add(Section("oops"))  # type: ignore[arg-type]
    if "Report" not in str(exc_info.value):
        raise AssertionError(exc_info.value)


def test_e2e_wif_chapter_add_chapter_raises() -> None:
    """Requirement: Chapter.add raises InvalidChildError for Chapter args.

    What-if: a caller tries to nest one Chapter inside another.  Chapters
    can only appear as direct children of Report.
    """
    with pytest.raises(InvalidChildError):
        Chapter("Outer").add(Chapter("Inner"))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Scenario 2 — Full content element type matrix
# ---------------------------------------------------------------------------


def test_e2e_all_content_elements_render_correct_markdown() -> None:
    """Requirement: every content element type renders its Markdown fragment.

    The user guide lists ten content element types.  Each rendered fragment
    must appear verbatim in the final document.
    """
    report = Report(title="Full").add(
        Chapter("Elements").add(
            Paragraph("Plain paragraph."),
            Paragraph(
                (
                    Text("bold", style="bold"),
                    LineBreak(),
                    Text("italic", style="italic"),
                    Text(" "),
                    Text("code", style="code"),
                    Text(" "),
                    Text("strike", style="strikethrough"),
                    Text(" plain"),
                ),
            ),
            CodeBlock("x = 1", language="python"),
            Table(
                headers=("A", "B"),
                rows=(("a1", "b1"), ("a2", "b2")),
            ),
            BulletList(("alpha", "beta")),
            NumberedList(("one", "two")),
            Image("img.png", alt="Alt", title="Title"),
            HorizontalRule(),
            BlockQuote("Quote line one.\nQuote line two."),
        ),
    )
    markdown = report.render()

    fragments = [
        "Plain paragraph.",
        "**bold**",
        "  \n",
        "*italic*",
        "`code`",
        "~~strike~~",
        "```python\nx = 1\n```",
        "| A | B |",
        "| a1 | b1 |",
        "- alpha",
        "1. one",
        '![Alt](img.png "Title")',
        "---",
        "> Quote line one.",
        "> Quote line two.",
    ]
    for fragment in fragments:
        if fragment not in markdown:
            msg = f"Expected fragment not found: {fragment!r}"
            raise AssertionError(msg)


def test_e2e_text_all_styles_render_correct_markers() -> None:
    """Requirement: each Text style inserts the documented Markdown markers.

    The user guide documents five styles: plain, bold, italic, code, and
    strikethrough.
    """
    cases = [
        (Text("x", style="plain"), "x"),
        (Text("x", style="bold"), "**x**"),
        (Text("x", style="italic"), "*x*"),
        (Text("x", style="code"), "`x`"),
        (Text("x", style="strikethrough"), "~~x~~"),
    ]
    for text_elem, expected in cases:
        result = text_elem.render()
        if result != expected:
            msg = f"style={text_elem.style!r}: got {result!r}"
            raise AssertionError(msg)


def test_e2e_text_empty_content_is_accepted() -> None:
    """Requirement: Text accepts an empty string and renders an empty span.

    The user guide states Text content may be empty, which is useful when
    building conditional paragraphs programmatically.
    """
    result = Text("", style="bold").render()
    if result != "****":
        raise AssertionError(result)


def test_e2e_link_renders_inline_in_paragraph() -> None:
    """Requirement: Link renders as [text](url) inside a Paragraph tuple.

    Link is an inline element and must be placed inside a Paragraph
    tuple to be used inside a Chapter or Section.
    """
    report = Report("R").add(
        Chapter("C").add(
            Paragraph(
                (Text("See "), Text("https://example.com", style="plain")),
            ),
        ),
    )
    markdown = report.render()
    if "https://example.com" not in markdown:
        raise AssertionError(markdown)


def test_e2e_link_with_title_renders_quoted_title() -> None:
    """Requirement: Link renders an optional title as a quoted attribute.

    The user guide shows [text](url "title") syntax when a title is given.
    """
    from mkforge import Link  # noqa: PLC0415

    result = Link("https://a.com", text="A", title="Hover").render()
    expected = '[A](https://a.com "Hover")'
    if result != expected:
        raise AssertionError(result)


def test_e2e_link_without_text_renders_empty_brackets() -> None:
    """Requirement: Link with no text produces [](url) syntax.

    The user guide documents that the text argument defaults to an empty
    string, allowing URL-only links.
    """
    from mkforge import Link  # noqa: PLC0415

    result = Link("https://a.com").render()
    if result != "[](https://a.com)":
        raise AssertionError(result)


def test_e2e_blockquote_multiline_prefixes_all_lines() -> None:
    """Requirement: BlockQuote prefixes every line with '> '.

    The user guide shows multi-line content is supported and each line
    receives a separate '> ' prefix.
    """
    result = BlockQuote("Line A.\nLine B.").render()
    expected = "> Line A.\n> Line B."
    if result != expected:
        raise AssertionError(result)


def test_e2e_codeblock_without_language_has_plain_fence() -> None:
    """Requirement: CodeBlock without a language produces a plain fence.

    The user guide states the language hint is optional and defaults to
    an empty string, producing a plain ``` fence.
    """
    result = CodeBlock("x = 1").render()
    if result != "```\nx = 1\n```":
        raise AssertionError(result)


def test_e2e_table_headers_only_renders_two_lines() -> None:
    """Requirement: Table with no rows renders headers + separator only.

    The user guide states rows defaults to an empty tuple.  A header-only
    table must produce exactly two pipe-delimited lines.
    """
    lines = Table(headers=("Col1", "Col2")).render().splitlines()
    if lines[0] != "| Col1 | Col2 |":
        raise AssertionError(lines)
    if lines[1] != "| --- | --- |":
        raise AssertionError(lines)
    if len(lines) != _TWO_LINES:
        raise AssertionError(lines)


def test_e2e_table_from_columns_renders_rows() -> None:
    """Requirement: Table can be built from column-oriented data.

    Users often hold tabular data as named columns.  The class method
    transposes those columns into GFM rows while preserving header order.
    """
    table = Table.from_columns(
        {
            "Check": ("format", "tests"),
            "Status": ("pass", "pass"),
        },
    )
    expected = (
        "| Check | Status |\n"
        "| --- | --- |\n"
        "| format | pass |\n"
        "| tests | pass |"
    )
    result = table.render()
    if result != expected:
        raise AssertionError(result)


def test_e2e_wif_paragraph_empty_string_raises() -> None:
    """Requirement: Paragraph rejects an empty plain string.

    What-if: a caller passes an empty string.  An empty paragraph would
    produce invisible content and confuse Markdown renderers.
    """
    with pytest.raises(ValueError, match="Paragraph content cannot be empty"):
        Paragraph("")


def test_e2e_wif_paragraph_list_instead_of_tuple_raises() -> None:
    """Requirement: Paragraph inline content must be a tuple, not a list.

    What-if: a caller passes a list.  The contract requires a tuple so
    that Paragraph instances are immutable.
    """
    with pytest.raises(TypeError, match="must be a tuple"):
        Paragraph([Text("x")])  # type: ignore[arg-type]


def test_e2e_wif_paragraph_invalid_inline_type_raises() -> None:
    """Requirement: Paragraph tuple items must be Text, LineBreak, or Link.

    What-if: a caller inserts a raw string into the inline tuple.  Only
    typed inline elements are accepted to prevent silent rendering errors.
    """
    with pytest.raises(TypeError, match="Text, LineBreak, or Link"):
        Paragraph(("raw string",))  # type: ignore[arg-type]


def test_e2e_wif_text_invalid_style_raises() -> None:
    """Requirement: Text rejects an unknown style name.

    What-if: a caller passes a style not in the documented set.  ValueError
    must be raised immediately at construction time, not at render time.
    """
    with pytest.raises(ValueError, match="Text style must be one of"):
        Text("x", style="underline")  # type: ignore[arg-type]


def test_e2e_wif_image_empty_path_raises() -> None:
    """Requirement: Image requires a non-empty path or URL.

    What-if: a caller passes an empty string as the image path.  An image
    with no path would produce broken Markdown syntax.
    """
    with pytest.raises(ValueError, match="Image path cannot be empty"):
        Image("")


def test_e2e_wif_bullet_list_empty_tuple_raises() -> None:
    """Requirement: BulletList rejects an empty tuple.

    What-if: a caller passes an empty tuple.  An empty list element would
    produce a Markdown block with no items, which is invalid GFM.
    """
    with pytest.raises(
        ValueError,
        match="BulletList must contain at least one item",
    ):
        BulletList(())


def test_e2e_wif_bullet_list_non_tuple_raises() -> None:
    """Requirement: BulletList items must be a tuple, not a list.

    What-if: a caller passes a list.  BulletList must be immutable, so
    a tuple is required by the constructor.
    """
    with pytest.raises(TypeError, match="BulletList items must be a tuple"):
        BulletList(["item"])  # type: ignore[arg-type]


def test_e2e_wif_numbered_list_empty_tuple_raises() -> None:
    """Requirement: NumberedList rejects an empty tuple.

    What-if: a caller passes an empty tuple.  An ordered list with no
    items is semantically empty and must be rejected at construction time.
    """
    with pytest.raises(
        ValueError,
        match="NumberedList must contain at least one item",
    ):
        NumberedList(())


def test_e2e_wif_table_empty_headers_raises() -> None:
    """Requirement: Table requires at least one header column.

    What-if: a caller passes an empty tuple as headers.  A table without
    column headers cannot be rendered as valid GFM.
    """
    with pytest.raises(
        InvalidTableError,
        match="Table headers cannot be empty",
    ):
        Table(())


def test_e2e_wif_table_row_wrong_cell_count_raises() -> None:
    """Requirement: each Table row must match the header cell count.

    What-if: a row has fewer cells than the header.  GFM pipe tables
    require consistent column counts across all rows.
    """
    with pytest.raises(InvalidTableError, match="Row 0 has 1 cells"):
        Table(("A", "B"), (("only_one",),))


def test_e2e_wif_table_non_tuple_headers_raises() -> None:
    """Requirement: Table headers must be a tuple, not a list.

    What-if: a caller passes a list.  The Table contract requires immutable
    input so that frozen-dataclass semantics are preserved.
    """
    with pytest.raises(TypeError, match="Table headers must be a tuple"):
        Table(["A", "B"])  # type: ignore[arg-type]


def test_e2e_wif_table_from_columns_empty_mapping_raises() -> None:
    """Requirement: Table.from_columns requires at least one column.

    What-if: a caller passes an empty mapping.  The result would have no
    headers, which is invalid for a GFM pipe table.
    """
    with pytest.raises(
        InvalidTableError,
        match="Table headers cannot be empty",
    ):
        Table.from_columns({})


def test_e2e_wif_table_from_columns_non_mapping_raises() -> None:
    """Requirement: Table.from_columns requires a mapping.

    What-if: a caller passes row data or another sequence.  Column-oriented
    construction must fail with a clear boundary error.
    """
    with pytest.raises(TypeError, match="Table columns must be a mapping"):
        Table.from_columns([("A", ("x",))])  # type: ignore[arg-type]


def test_e2e_wif_table_from_columns_non_tuple_column_raises() -> None:
    """Requirement: Table.from_columns column values must be tuples.

    What-if: a caller passes a list of cells.  The Table API preserves
    immutable tuple inputs, matching the row-oriented constructor.
    """
    with pytest.raises(TypeError, match="Table column A must be a tuple"):
        Table.from_columns({"A": ["x"]})  # type: ignore[dict-item]


def test_e2e_wif_table_from_columns_mismatched_lengths_raises() -> None:
    """Requirement: Table.from_columns columns must have equal lengths.

    What-if: one column contains fewer cells.  The data cannot be transposed
    into rectangular GFM rows, so construction raises InvalidTableError.
    """
    with pytest.raises(
        InvalidTableError,
        match="Table columns must all have the same number of cells",
    ):
        Table.from_columns({"A": ("x",), "B": ("y", "z")})


# ---------------------------------------------------------------------------
# Scenario 3 — YAML frontmatter, TOC, and auto-numbering
# ---------------------------------------------------------------------------


def test_e2e_frontmatter_renders_all_supported_value_types() -> None:
    """Requirement: metadata dict renders each Python type to valid YAML.

    The user guide documents str, int, float, bool, None, and list/tuple.
    Each must produce the exact YAML representation shown in the guide.
    """
    report = Report(
        title="Doc",
        metadata={
            "title": "Doc",
            "count": 42,
            "ratio": 0.5,
            "active": True,
            "archived": False,
            "notes": None,
            "tags": ["a", "b"],
        },
    )
    markdown = report.render()

    for fragment in [
        "title: Doc",
        "count: 42",
        "ratio: 0.5",
        "active: true",
        "archived: false",
        "notes: null",
        "tags:",
        "  - a",
        "  - b",
    ]:
        if fragment not in markdown:
            msg = f"Missing fragment {fragment!r}"
            raise AssertionError(msg)
    if not markdown.startswith("---\n"):
        raise AssertionError(markdown[:40])


def test_e2e_toc_lists_chapters_and_sections_with_anchors() -> None:
    """Requirement: toc=True generates anchored links for every heading.

    A report with a two-level tree must produce a nested Markdown list
    after the H1 title.
    """
    report = Report(title="Doc", toc=True).add(
        Chapter("Overview").add(
            Section("Background"),
            Section("Scope"),
        ),
        Chapter("Results"),
    )
    markdown = report.render()

    for entry in [
        "- [Overview](#overview)",
        "  - [Background](#background)",
        "  - [Scope](#scope)",
        "- [Results](#results)",
    ]:
        if entry not in markdown:
            msg = f"Missing TOC entry {entry!r}"
            raise AssertionError(msg)


def test_e2e_auto_numbering_prefixes_all_heading_levels() -> None:
    """Requirement: auto_numbering=True prefixes headings with dotted counters.

    The user guide shows headings rendered as '1.', '1.1.', '1.2.', etc.
    """
    report = Report(title="Doc", auto_numbering=True).add(
        Chapter("Alpha").add(
            Section("Sub One"),
            Section("Sub Two"),
        ),
        Chapter("Beta"),
    )
    markdown = report.render()

    for heading in [
        "## 1. Alpha",
        "### 1.1. Sub One",
        "### 1.2. Sub Two",
        "## 2. Beta",
    ]:
        if heading not in markdown:
            msg = f"Missing heading {heading!r}"
            raise AssertionError(msg)


def test_e2e_toc_and_auto_numbering_together() -> None:
    """Requirement: toc and auto_numbering flags are independent.

    When both are enabled, the TOC uses the original un-numbered title
    for anchor generation while headings carry dotted prefixes.
    """
    report = Report(title="Doc", toc=True, auto_numbering=True).add(
        Chapter("Overview").add(Section("Scope")),
    )
    markdown = report.render()

    if "- [Overview](#overview)" not in markdown:
        raise AssertionError(markdown)
    if "  - [Scope](#scope)" not in markdown:
        raise AssertionError(markdown)
    if "## 1. Overview" not in markdown:
        raise AssertionError(markdown)
    if "### 1.1. Scope" not in markdown:
        raise AssertionError(markdown)


def test_e2e_anchor_slug_normalises_titles() -> None:
    """Requirement: anchor_slug produces GitHub-compatible anchor strings.

    TOC links rely on anchor_slug.  Titles with mixed case and spaces must
    produce the expected lowercase hyphen form.
    """
    cases = [
        ("Hello World", "hello-world"),
        ("  Spaces  ", "spaces"),
    ]
    for title, expected in cases:
        result = anchor_slug(title)
        if result != expected:
            msg = f"anchor_slug({title!r}) = {result!r}, want {expected!r}"
            raise AssertionError(msg)


def test_e2e_wif_metadata_non_dict_raises() -> None:
    """Requirement: Report rejects non-dict metadata.

    What-if: a caller passes a string.  The metadata argument must be a
    dict so that keys can be validated individually.
    """
    with pytest.raises(TypeError, match="metadata must be a dict"):
        Report("Bad", metadata="not-a-dict")  # type: ignore[arg-type]


def test_e2e_wif_metadata_non_string_key_raises() -> None:
    """Requirement: Report rejects metadata with non-string keys.

    What-if: a caller passes an integer key.  YAML frontmatter keys must
    be strings to produce valid YAML output.
    """
    with pytest.raises(TypeError, match="metadata keys must be a string"):
        Report("Bad", metadata={1: "value"})  # type: ignore[dict-item]


def test_e2e_wif_toc_non_bool_raises() -> None:
    """Requirement: Report toc argument must be a bool.

    What-if: a caller passes an integer.  The toc flag must be a strict
    bool to avoid ambiguous truthy coercion.
    """
    with pytest.raises(TypeError, match="Report toc must be a bool"):
        Report("Bad", toc=1)  # type: ignore[arg-type]


def test_e2e_wif_auto_numbering_non_bool_raises() -> None:
    """Requirement: Report auto_numbering argument must be a bool.

    What-if: a caller passes a string.  The flag must be a strict bool
    to avoid truthy coercion.
    """
    with pytest.raises(
        TypeError,
        match="Report auto_numbering must be a bool",
    ):
        Report("Bad", auto_numbering="yes")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Scenario 4 — Section nesting up to and beyond H6 limit
# ---------------------------------------------------------------------------


def test_e2e_section_nesting_h3_to_h6_renders_correct_levels() -> None:
    """Requirement: sections render as H3, H4, H5, H6 at increasing depths.

    The user guide maps depth 1→H3, 2→H4, 3→H5, 4→H6.
    """
    report = Report(title="Deep").add(
        Chapter("Root").add(
            Section("L1").add(
                Section("L2").add(
                    Section("L3").add(
                        Section("L4"),
                    ),
                ),
            ),
        ),
    )
    markdown = report.render()

    for heading in ["### L1", "#### L2", "##### L3", "###### L4"]:
        if heading not in markdown:
            msg = f"Missing heading {heading!r}"
            raise AssertionError(msg)


def test_e2e_wif_section_depth_exceeds_h6_raises_at_render() -> None:
    """Requirement: sections beyond H6 depth raise ReportDepthError.

    What-if: the tree has 5 nested sections below a chapter, requiring
    an H7 heading.  The tree builds successfully but rendering must fail
    with a clear error before producing invalid Markdown.
    """
    report = Report(title="Deep").add(
        Chapter("Root").add(
            Section("L1").add(
                Section("L2").add(
                    Section("L3").add(
                        Section("L4").add(
                            Section("L5"),
                        ),
                    ),
                ),
            ),
        ),
    )
    with pytest.raises(ReportDepthError, match="H7"):
        report.render()


def test_e2e_wif_section_add_chapter_raises() -> None:
    """Requirement: Section.add raises InvalidChildError for Chapter args.

    What-if: a caller tries to nest a Chapter inside a Section.  Chapters
    can only appear as direct children of Report.
    """
    with pytest.raises(InvalidChildError):
        Section("S").add(Chapter("C"))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Scenario 5 — Save to file and read back content
# ---------------------------------------------------------------------------


def test_e2e_save_creates_file_with_correct_content(tmp_path: Path) -> None:
    """Requirement: save() writes a UTF-8 file matching render() output.

    A user calls report.save(path) and reads back the file; the content
    must be byte-for-byte identical to report.render().
    """
    report = Report(title="Saved").add(
        Chapter("C").add(Paragraph("Hello from file.")),
    )
    output = tmp_path / "report.md"
    report.save(output)

    content = output.read_text(encoding="utf-8")
    if content != report.render():
        raise AssertionError(content)


def test_e2e_save_creates_parent_directories(tmp_path: Path) -> None:
    """Requirement: save() creates intermediate directories automatically.

    The user guide states save() creates parent directories as needed.
    No manual mkdir should be required before calling save().
    """
    output = tmp_path / "nested" / "deep" / "report.md"
    Report(title="Nested").save(output)

    if not output.exists():
        msg = f"File not created at {output}"
        raise AssertionError(msg)


def test_e2e_save_accepts_string_path(tmp_path: Path) -> None:
    """Requirement: save() accepts a plain string as the path argument.

    The user guide documents both str and Path as valid path types.
    """
    output = str(tmp_path / "report.md")
    Report(title="String").save(output)

    if not Path(output).exists():
        msg = f"File not created at {output}"
        raise AssertionError(msg)


def test_e2e_wif_save_empty_string_path_raises() -> None:
    """Requirement: save() rejects an empty string path.

    What-if: a caller passes an empty string.  An empty path cannot refer
    to any file and must be rejected immediately.
    """
    with pytest.raises(ValueError, match="save path cannot be empty"):
        Report("Bad").save("")


def test_e2e_wif_save_non_string_path_raises() -> None:
    """Requirement: save() rejects a path that is neither str nor PathLike.

    What-if: a caller passes an integer.  Only string and PathLike types
    are documented as valid path arguments.
    """
    with pytest.raises(TypeError, match="save path must be str or PathLike"):
        Report("Bad").save(123)  # type: ignore[arg-type]


def test_e2e_wif_render_non_report_raises() -> None:
    """Requirement: render_report() rejects non-Report objects.

    What-if: a caller passes a plain dict.  TypeError must be raised so
    that misuse is caught at the call site.
    """
    with pytest.raises(TypeError, match="report must be a Report"):
        render_report({"title": "dict"})


# ---------------------------------------------------------------------------
# Scenario 6 — Asset verification before save
# ---------------------------------------------------------------------------


def test_e2e_save_raises_missing_asset_for_absent_image(
    tmp_path: Path,
) -> None:
    """Requirement: save() raises MissingAssetError for absent local images.

    A user who references a local image must ensure the file exists before
    calling save().  The error exposes the missing path.
    """
    report = Report(title="Assets").add(
        Chapter("C").add(Image("missing_chart.png", alt="Chart")),
    )
    output = tmp_path / "report.md"

    with pytest.raises(MissingAssetError) as exc_info:
        report.save(output)

    if not exc_info.value.missing:
        raise AssertionError(exc_info.value.missing)
    if not any("missing_chart.png" in str(p) for p in exc_info.value.missing):
        raise AssertionError(exc_info.value.missing)


def test_e2e_save_succeeds_when_local_image_exists(tmp_path: Path) -> None:
    """Requirement: save() completes when all local image paths exist on disk.

    This is the happy path: the user creates the image file before saving.
    No exception should be raised.
    """
    image_file = tmp_path / "chart.png"
    image_file.write_bytes(b"\x89PNG")

    report = Report(title="Assets").add(
        Chapter("C").add(Image(str(image_file), alt="Chart")),
    )
    output = tmp_path / "report.md"
    report.save(output)

    if not output.exists():
        msg = f"File not created at {output}"
        raise AssertionError(msg)


def test_e2e_remote_image_not_checked_locally(tmp_path: Path) -> None:
    """Requirement: remote image URLs are not checked for local existence.

    The user guide states only local paths are verified; remote URLs
    containing '://' are not looked up on disk.
    """
    report = Report(title="Remote").add(
        Chapter("C").add(
            Image("https://example.com/logo.png", alt="Logo"),
        ),
    )
    output = tmp_path / "report.md"
    report.save(output)

    if not output.exists():
        msg = f"File not created at {output}"
        raise AssertionError(msg)


def test_e2e_wif_missing_asset_error_missing_is_tuple() -> None:
    """Requirement: MissingAssetError.missing is a tuple of Path objects.

    What-if: code catches MissingAssetError and iterates over .missing.
    The attribute must be a tuple of Path values regardless of the list
    passed to the constructor.
    """
    from mkforge.errors import MissingAssetError as _Err  # noqa: PLC0415

    err = _Err([Path("/a/b.png"), Path("/c/d.png")])
    if not isinstance(err.missing, tuple):
        raise TypeError(type(err.missing))
    if not all(isinstance(p, Path) for p in err.missing):
        raise TypeError(err.missing)


# ---------------------------------------------------------------------------
# Scenario 7 — Asset copy with local images
# ---------------------------------------------------------------------------


def test_e2e_save_copy_assets_copies_image_to_assets_dir(
    tmp_path: Path,
) -> None:
    """Requirement: copy_assets=True copies local images into assets/ dir.

    A user who wants a self-contained output directory passes
    copy_assets=True.  The image must be present at assets/<name> after
    save() completes.
    """
    image_file = tmp_path / "src" / "logo.png"
    image_file.parent.mkdir()
    image_file.write_bytes(b"\x89PNG")

    output = tmp_path / "out" / "report.md"
    report = Report(title="Copy").add(
        Chapter("C").add(Image(str(image_file), alt="Logo")),
    )
    report.save(output, copy_assets=True)

    assets_dir = output.parent / "assets"
    if not assets_dir.is_dir():
        msg = f"assets/ not created at {assets_dir}"
        raise AssertionError(msg)
    copied = list(assets_dir.iterdir())
    if len(copied) != 1:
        raise AssertionError(copied)
    if copied[0].name != "logo.png":
        raise AssertionError(copied[0].name)


def test_e2e_save_copy_assets_rewrites_image_link(tmp_path: Path) -> None:
    """Requirement: copy_assets=True rewrites image links to assets/ paths.

    After copy_assets, image references must point inside assets/ rather
    than to the original source path.
    """
    image_file = tmp_path / "original.png"
    image_file.write_bytes(b"\x89PNG")

    output = tmp_path / "report.md"
    report = Report(title="Rewrite").add(
        Chapter("C").add(Image(str(image_file), alt="Img")),
    )
    report.save(output, copy_assets=True)

    content = output.read_text(encoding="utf-8")
    if "assets/original.png" not in content:
        raise AssertionError(content)


# ---------------------------------------------------------------------------
# Scenario 8 — Verify conformant Markdown string
# ---------------------------------------------------------------------------


def test_e2e_verify_clean_markdown_passes() -> None:
    """Requirement: verify_markdown on well-formed Markdown returns passed.

    A user who generates a report and wants to gate CI on Markdown quality
    can call verify_markdown.  Clean output must produce no diagnostics.
    """
    source = textwrap.dedent("""\
        # Title

        A paragraph of text.

        | Col A | Col B |
        | --- | --- |
        | one | two |

        - bullet one
        - bullet two
    """)
    result = verify_markdown(
        source,
        settings=VerificationSettings(disabled=frozenset({"MD013"})),
    )

    if not isinstance(result, VerificationReport):
        raise TypeError(type(result))
    if result.rule_set_name != "markdown-compliance":
        raise AssertionError(result.rule_set_name)
    if not result.passed:
        raise AssertionError([d.message for d in result.diagnostics])
    if result.diagnostics != ():
        raise AssertionError(result.diagnostics)


def test_e2e_verify_generated_report_output_passes() -> None:
    """Requirement: Markdown generated by MkForge passes its own verifier.

    A user who uses MkForge to generate reports and also to verify Markdown
    quality should get a passing report when both features are combined.
    """
    report = Report(title="Audit").add(
        Chapter("Results").add(
            Section("Summary").add(
                Paragraph("All checks passed."),
                Table(
                    headers=("Check", "Status"),
                    rows=(("lint", "ok"),),
                ),
            ),
        ),
    )
    markdown = report.render()
    disabled = frozenset({"MD013", "MD018", "MD047"})
    result = verify_markdown(
        markdown,
        settings=VerificationSettings(disabled=disabled),
    )

    if not result.passed:
        raise AssertionError([d.message for d in result.diagnostics])


# ---------------------------------------------------------------------------
# Scenario 9 — Verify non-conformant Markdown string
# ---------------------------------------------------------------------------


def test_e2e_verify_detects_missing_space_in_atx_heading() -> None:
    """Requirement: verify_markdown detects MD018 (no space after '#').

    A user who hand-writes Markdown and omits the space after '#' should
    see an MD018 diagnostic pointing to the exact line.
    """
    result = verify_markdown("#Missing space\n")

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MD018" not in rule_ids:
        raise AssertionError(result.diagnostics)
    if result.passed:
        raise AssertionError(result.diagnostics)


def test_e2e_verify_detects_bare_url() -> None:
    """Requirement: verify_markdown detects MD034 (bare URL in text).

    MD034 flags raw URLs not inside angle brackets or Markdown link syntax.
    """
    source = "# Title\n\nSee http://example.com for details.\n"
    result = verify_markdown(source)

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "MD034" not in rule_ids:
        raise AssertionError(result.diagnostics)


def test_e2e_verify_detects_gfm_table_delimiter_error() -> None:
    """Requirement: verify_markdown detects GFM001 (bad table delimiter).

    GFM requires at least three dashes per delimiter cell.  A delimiter
    with fewer dashes must trigger GFM001.
    """
    source = "| A | B |\n| -- | - |\n| x | y |\n"
    result = verify_markdown(
        source,
        settings=VerificationSettings(disabled=frozenset({"MD041"})),
    )

    rule_ids = {d.rule_id for d in result.diagnostics}
    if "GFM001" not in rule_ids:
        raise AssertionError(result.diagnostics)


def test_e2e_verify_reports_all_violations_in_one_pass() -> None:
    """Requirement: verify_markdown reports all violations in a single pass.

    Multiple issues in a document must all appear in the diagnostics tuple.
    The verification run is not stopped on the first error encountered.
    """
    source = "#MissingSpace\n#Also missing\n(wrong)[https://example.com]\n"
    result = verify_markdown(source)

    rule_ids = {d.rule_id for d in result.diagnostics}
    if len(result.diagnostics) < _THREE_LINES:
        raise AssertionError(result.diagnostics)
    if "MD018" not in rule_ids:
        raise AssertionError(result.diagnostics)
    if "MD011" not in rule_ids:
        raise AssertionError(result.diagnostics)
