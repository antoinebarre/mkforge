"""End-to-end demonstration of mkforge verification and validation."""

from __future__ import annotations

from mkforge import verify, validate
from mkforge.verification.profiles import GFM_PROFILE, MARKDOWN_PROFILE
from mkforge.diagnostics import Diagnostic


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_WIDTH = 72
_SEP = "─" * _WIDTH


def _header(title: str) -> None:
    print()
    print(_SEP)
    print(f"  {title}")
    print(_SEP)


def _section(title: str) -> None:
    print(f"\n  {'·' * 3}  {title}")
    print()


def _show_source(source: str) -> None:
    print("  SOURCE")
    print("  " + "┌" + "─" * (_WIDTH - 4) + "┐")
    for i, line in enumerate(source.splitlines(), 1):
        truncated = line[:_WIDTH - 10]
        suffix = "…" if len(line) > _WIDTH - 10 else ""
        print(f"  │ {i:>3}  {truncated}{suffix}")
    print("  " + "└" + "─" * (_WIDTH - 4) + "┘")
    print()


def _show_diagnostics(
    diagnostics: tuple[Diagnostic, ...],
    label: str = "DIAGNOSTICS",
) -> None:
    print(f"  {label}  ({len(diagnostics)} found)")
    if not diagnostics:
        print("  ✓  No issues found.")
        return
    print()
    for d in diagnostics:
        print(f"  [{d.rule_id}]  line {d.line:>3}  {d.name}")
        print(f"           {d.message}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# PART 1 — VERIFICATION  (Markdown syntax, CommonMark + GFM)
# ─────────────────────────────────────────────────────────────────────────────

_header("PART 1 · VERIFICATION — Markdown syntax checks")

print("""
  verify() checks the raw Markdown source against syntax rules.
  Two profiles are available:
    • "markdown"  — CommonMark rules only (35 rules, MKV001–MKV035)
    • "gfm"       — CommonMark + GitHub Flavored Markdown (+ 5 MKG rules)

  Rules cover: heading levels, spacing, indentation, list markers,
  fenced code blocks, inline styles, references, links, GFM tables…
""")


# ── 1a. Clean source ────────────────────────────────────────────────────────

_section("1a — Clean source (no issues expected)")

CLEAN = """\
# Getting Started

Welcome to the project. This guide explains how to install and use
the library from scratch.

Run the following command to install:

```sh

pip install mkforge

```

Then import the library and call `verify()` on your Markdown source.

See the [documentation](https://example.com) for details.
"""

_show_source(CLEAN)
_show_diagnostics(verify(CLEAN))


# ── 1b. Many violations at once ─────────────────────────────────────────────

_section("1b — Source with many syntax violations")

DIRTY = """\
#Bad heading — no space after #
# Title
### Skipped level
Text
\tLine with a tab
(reversed)[link]
This line is intentionally very long and exceeds the configured limit
# Another title



Three blank lines above
* Item one
  * indented
* Item two
> blockquote
> continuation
```
no language
```
paragraph
<div>raw html</div>
---
***
* bullet *spaced emphasis*
` code with spaces `
[ link with spaces ](url)
    indented code block
~~~py
mixed fence
~~~
*em* and _em_
**strong** and __strong__
[use][missing-ref]
[unused-ref]: https://example.com
bare http://example.com
| A | B |
| - |
text without | leading pipe
"""

_show_source(DIRTY)
_show_diagnostics(
    verify(DIRTY, config={"MKV010": {"line_length": 60}}),
)


# ── 1c. Profile comparison: markdown vs gfm ─────────────────────────────────

_section("1c — Profile comparison on a GFM-specific source")

GFM_SOURCE = """\
# Title

bare http://example.com

| Name | Value |
| - |
| foo | bar |
"""

_show_source(GFM_SOURCE)

md_diags = verify(GFM_SOURCE, profile=MARKDOWN_PROFILE)
gfm_diags = verify(GFM_SOURCE, profile=GFM_PROFILE)

_show_diagnostics(md_diags, label=f'DIAGNOSTICS  profile="{MARKDOWN_PROFILE}"')
_show_diagnostics(gfm_diags, label=f'DIAGNOSTICS  profile="{GFM_PROFILE}"')
print("  → MKG001 (bare URL) and MKG003 (table column count) only in GFM.")


# ── 1d. Disabling specific rules ────────────────────────────────────────────

_section("1d — Disabling specific rules")

TABS_SOURCE = """\
# Title

\tThis line has a tab.
\tSo does this one.
"""

_show_source(TABS_SOURCE)
print("  With MKV007 (tabs) enabled:")
_show_diagnostics(verify(TABS_SOURCE))
print("  With MKV007 (tabs) disabled:")
_show_diagnostics(verify(TABS_SOURCE, disabled={"MKV007"}))


# ── 1e. Configurable rule: line length ──────────────────────────────────────

_section("1e — Configurable rule: MKV010 line length")

LENGTH_SOURCE = """\
# Title

Short line.

This line is seventy-five characters long and has a space at the end here x

This line is deliberately over eighty chars and has words after that boundary mark right here
"""

_show_source(LENGTH_SOURCE)
for limit in (80, 70):
    diags = verify(LENGTH_SOURCE, config={"MKV010": {"line_length": limit}})
    label = f"DIAGNOSTICS  line_length={limit}"
    _show_diagnostics(diags, label=label)


# ─────────────────────────────────────────────────────────────────────────────
# PART 2 — VALIDATION  (document content policy)
# ─────────────────────────────────────────────────────────────────────────────

_header("PART 2 · VALIDATION — Document content policy checks")

print("""
  validate() checks document-level content policies.
  13 rules (MKC001–MKC013) cover: heading uniqueness, title presence,
  heading punctuation, emphasis in headings, fenced code language tags,
  empty links, required heading structure, proper name casing,
  image alt text, link fragments, link style, and descriptive link text.

  These rules apply regardless of Markdown profile.
""")


# ── 2a. Clean document ──────────────────────────────────────────────────────

_section("2a — Clean document (no issues expected)")

VALID_DOC = """\
# Getting Started

This document describes how to install and configure Python.

## Prerequisites

You need Python 3.11 or later.

## Installation

Run the installer:

```sh
pip install mkforge
```

## Configuration

See the [configuration guide](https://docs.example.com/config).

![Architecture overview](diagram.png "Architecture diagram")
"""

_show_source(VALID_DOC)
_show_diagnostics(validate(VALID_DOC))


# ── 2b. Multiple content violations ─────────────────────────────────────────

_section("2b — Document with many content violations")

INVALID_DOC = """\
## No title at the top

# Duplicate heading

# Duplicate heading

### *Emphasized heading*

### Heading with punctuation.

```
missing language tag
```

Check [this]() for details.

See the [click here](https://example.com) page.

![](no-alt-text.png)

We use python for scripting and github for hosting.
"""

_show_source(INVALID_DOC)
_show_diagnostics(validate(INVALID_DOC))


# ── 2c. Configurable: required heading structure ─────────────────────────────

_section("2c — MKC008: required heading structure")

WRONG_STRUCTURE = """\
# My Project

## Contributing

Some content.
"""

REQUIRED = ["# My Project", "## Overview", "## Installation"]

_show_source(WRONG_STRUCTURE)
print(f"  Required headings: {REQUIRED}")
print()
_show_diagnostics(
    validate(WRONG_STRUCTURE, config={"MKC008": {"headings": REQUIRED}}),
)


# ── 2d. Configurable: proper name casing ────────────────────────────────────

_section("2d — MKC009: proper name casing")

CASING_DOC = """\
# Setup Guide

Install github desktop and configure python.
Then open github.com in your browser.
"""

NAMES = ["GitHub", "Python"]

_show_source(CASING_DOC)
print(f"  Proper names enforced: {NAMES}")
print()
_show_diagnostics(
    validate(CASING_DOC, config={"MKC009": {"names": NAMES}}),
)


# ── 2e. Configurable: link style enforcement ─────────────────────────────────

_section("2e — MKC012: link style enforcement")

LINK_DOC = """\
# Links

Inline link: [mkforge](https://github.com/example/mkforge).

Full-reference link: [mkforge][mkforge-ref].

[mkforge-ref]: https://github.com/example/mkforge
"""

_show_source(LINK_DOC)

print("  Forbid inline links (inline=False):")
_show_diagnostics(
    validate(LINK_DOC, config={"MKC012": {"inline": False}}),
)

print("  Forbid full-reference links (full=False):")
_show_diagnostics(
    validate(LINK_DOC, config={"MKC012": {"full": False}}),
)


# ── 2f. Combining verify + validate ─────────────────────────────────────────

_section("2f — Combined: verify + validate on the same source")

COMBINED = """\
## Not a title

# Duplicate

# Duplicate

Text
\tTabbed line

See [click here](https://example.com) and install python.
"""

_show_source(COMBINED)

v_diags = verify(COMBINED)
c_diags = validate(
    COMBINED,
    config={"MKC009": {"names": ["Python"]}},
)

_show_diagnostics(v_diags, label="VERIFICATION DIAGNOSTICS")
_show_diagnostics(c_diags, label="VALIDATION DIAGNOSTICS")

total = len(v_diags) + len(c_diags)
print(f"  Total: {len(v_diags)} verification + {len(c_diags)} validation"
      f" = {total} diagnostics")

print()
print(_SEP)
print("  Done.")
print(_SEP)
print()
