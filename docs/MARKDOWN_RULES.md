# MkForge Markdown Verification Rules

MkForge implements the markdownlint rule matrix from `RULES.md` and adds one
MkForge-specific file-resource rule.

Verification reads settings from `.mkforge`, `.mkforge.toml`, or
`pyproject.toml`. When both exist in the same directory, values are merged in
this order:

1. `pyproject.toml`
2. `.mkforge.toml`
3. `.mkforge`

For `pyproject.toml`, use `[tool.mkforge.verification]`. For `.mkforge`, use
`[verification]`.

```toml
[verification]
disabled = ["MD013", "MD033"]

[verification.rules.MD013]
line_length = 100
ignore_code_blocks = true

[verification.rules.MD033]
allowed_elements = "br,details,summary"
```

The same settings in `pyproject.toml`:

```toml
[tool.mkforge.verification]
disabled = ["MD013", "MD033"]

[tool.mkforge.verification.rules.MD013]
line_length = 100
ignore_code_blocks = true
```

## Rule Reference

### MD001 - Heading Increment

Headings should not skip levels.

Bad:

```markdown
# Chapter
### Deep section
```

Good:

```markdown
# Chapter
## Section
### Deep section
```

Default options:

```toml
[verification.rules.MD001]
front_matter_title = "^\\s*title\\s*[:=]"
```

### MD002 - First Heading Level

The first heading should use the configured top level.

Bad:

```markdown
## Starts too low
```

Good:

```markdown
# Starts at level one
```

Default options:

```toml
[verification.rules.MD002]
level = 1
front_matter_title = "^\\s*title\\s*[:=]"
```

### MD003 - Heading Style

Heading syntax should match the configured style.

Bad:

```markdown
# ATX

Setext
======
```

Good:

```markdown
# ATX

## Also ATX
```

Default options:

```toml
[verification.rules.MD003]
style = "consistent"
```

Accepted styles are `consistent`, `atx`, `atx_closed`, `setext`, and
`setext_with_atx`.

### MD004 - Unordered List Style

Unordered list markers should match the configured style.

Bad:

```markdown
* One
+ Two
- Three
```

Good:

```markdown
- One
- Two
- Three
```

Default options:

```toml
[verification.rules.MD004]
style = "consistent"
```

Accepted styles are `consistent`, `asterisk`, `plus`, `dash`, and `sublist`.

### MD005 - List Indentation Consistency

Items parsed at the same nesting level should align.

Bad:

```markdown
- One
  - Nested
   - Misaligned
```

Good:

```markdown
- One
   - Nested
   - Aligned
```

### MD006 - Top-Level Unordered List Starts Left

Top-level unordered list items should not be indented.

Bad:

```markdown
  - Top level item
```

Good:

```markdown
- Top level item
```

### MD007 - Unordered List Indentation

Nested unordered list indentation should use the configured width.

Bad:

```markdown
- One
  - Nested by two spaces
```

Good with the default:

```markdown
- One
   - Nested by three spaces
```

Default options:

```toml
[verification.rules.MD007]
indent = 3
```

### MD009 - Trailing Spaces

Lines should not end with stray spaces. The configured `br_spaces` value is
allowed for hard line breaks.

Bad:

```markdown
Text with three trailing spaces   
```

Good:

```markdown
Text without trailing spaces
```

Default options:

```toml
[verification.rules.MD009]
br_spaces = 2
```

### MD010 - Hard Tabs

Use spaces instead of tab characters.

Bad:

```markdown
	Indented with a tab
```

Good:

```markdown
    Indented with spaces
```

Default options:

```toml
[verification.rules.MD010]
ignore_code_blocks = false
```

### MD011 - Reversed Link Syntax

Link text belongs in brackets and the destination belongs in parentheses.

Bad:

```markdown
(Docs)[https://example.com]
```

Good:

```markdown
[Docs](https://example.com)
```

### MD012 - Multiple Blank Lines

Avoid repeated blank lines outside fenced code blocks.

Bad:

```markdown
One


Two
```

Good:

```markdown
One

Two
```

### MD013 - Line Length

Lines should fit within the configured length unless excluded.

Bad:

```markdown
This sentence is intentionally long enough to cross the configured limit.
```

Good:

```markdown
This sentence is split so that each source line remains readable.
```

Default options:

```toml
[verification.rules.MD013]
line_length = 80
ignore_code_blocks = false
code_blocks = true
tables = true
headings = true
treat_links_as_single_words = false
```

### MD014 - Command Prompts Without Output

Shell command examples should omit `$` prompts when no output is shown.

Bad:

```markdown
```sh
$ ls
$ pwd
```
```

Good:

```markdown
```sh
ls
pwd
```
```

### MD018 - Missing Space After ATX Marker

ATX headings require a space after the `#` marker.

Bad:

```markdown
#Heading
```

Good:

```markdown
# Heading
```

### MD019 - Multiple Spaces After ATX Marker

Use one space after an opening ATX marker.

Bad:

```markdown
#  Heading
```

Good:

```markdown
# Heading
```

### MD020 - Missing Space In Closed ATX Heading

Closed ATX headings need spaces inside both marker groups.

Bad:

```markdown
#Heading#
```

Good:

```markdown
# Heading #
```

### MD021 - Multiple Spaces In Closed ATX Heading

Closed ATX headings should use one inner space on each side.

Bad:

```markdown
#  Heading  #
```

Good:

```markdown
# Heading #
```

### MD022 - Blank Lines Around Headings

Headings should be separated from surrounding paragraphs.

Bad:

```markdown
Text
## Heading
More text
```

Good:

```markdown
Text

## Heading

More text
```

### MD023 - Headings Start At Column One

Indented ATX headings may be parsed as plain text.

Bad:

```markdown
  # Indented heading
```

Good:

```markdown
# Heading
```

### MD024 - Duplicate Headings

Duplicate headings can produce ambiguous generated anchors.

Bad:

```markdown
## Install
## Install
```

Good:

```markdown
## Install
## Configure
```

Default options:

```toml
[verification.rules.MD024]
allow_different_nesting = false
```

### MD025 - Multiple Top-Level Headings

Use one configured top-level heading for the document title.

Bad:

```markdown
# Title
# Another title
```

Good:

```markdown
# Title
## Section
```

Default options:

```toml
[verification.rules.MD025]
level = 1
front_matter_title = "^\\s*title\\s*[:=]"
```

### MD026 - Heading Trailing Punctuation

Headings should not end with configured punctuation.

Bad:

```markdown
# What changed?
```

Good:

```markdown
# What changed
```

Default options:

```toml
[verification.rules.MD026]
punctuation = ".,;:!?"
```

### MD027 - Blockquote Marker Spacing

Use one space after a blockquote marker.

Bad:

```markdown
>  Too much space
```

Good:

```markdown
> One space
```

### MD028 - Blank Line Inside Blockquote

Blank lines between adjacent blockquotes should keep the quote marker when they
belong to the same quote.

Bad:

```markdown
> First quote

> Still the same quote
```

Good:

```markdown
> First quote
>
> Still the same quote
```

### MD029 - Ordered List Prefix

Ordered list numbering should match the configured style.

Bad with default `one`:

```markdown
1. One
2. Two
```

Good with default `one`:

```markdown
1. One
1. Two
```

Default options:

```toml
[verification.rules.MD029]
style = "one"
```

Accepted styles are `one` and `ordered`.

### MD030 - List Marker Spacing

Use the configured number of spaces after list markers.

Bad:

```markdown
-  Too much space
1.  Too much space
```

Good:

```markdown
- One space
1. One space
```

Default options:

```toml
[verification.rules.MD030]
ul_single = 1
ol_single = 1
ul_multi = 1
ol_multi = 1
```

### MD031 - Blank Lines Around Fenced Code

Fenced code blocks should be separated from paragraphs.

Bad:

````markdown
Text
```python
print("hi")
```
Text
````

Good:

````markdown
Text

```python
print("hi")
```

Text
````

### MD032 - Blank Lines Around Lists

Lists should be separated from surrounding paragraphs.

Bad:

```markdown
Text
- item
Text
```

Good:

```markdown
Text

- item

Text
```

### MD033 - Inline HTML

Raw HTML is disabled unless the element is allow-listed.

Bad:

```markdown
<div>HTML</div>
```

Good:

```markdown
Plain Markdown text
```

Default options:

```toml
[verification.rules.MD033]
allowed_elements = ""
```

### MD034 - Bare URL

URLs should be written as autolinks or Markdown links.

Bad:

```markdown
See https://example.com
```

Good:

```markdown
See <https://example.com>
```

### MD035 - Horizontal Rule Style

Horizontal rules should match one style.

Bad:

```markdown
---
***
```

Good:

```markdown
---
---
```

Default options:

```toml
[verification.rules.MD035]
style = "consistent"
```

### MD036 - Emphasis Used As Heading

A standalone emphasized line is probably a heading.

Bad:

```markdown
**Overview**
```

Good:

```markdown
## Overview
```

Default options:

```toml
[verification.rules.MD036]
punctuation = ".,;:!?"
```

### MD037 - Spaces Inside Emphasis Markers

Remove spaces just inside emphasis markers.

Bad:

```markdown
This is ** bold ** text.
```

Good:

```markdown
This is **bold** text.
```

### MD038 - Spaces Inside Code Span Markers

Remove spaces just inside code span backticks.

Bad:

```markdown
` code `
```

Good:

```markdown
`code`
```

### MD039 - Spaces Inside Link Text

Remove spaces just inside link text brackets.

Bad:

```markdown
[ docs ](https://example.com)
```

Good:

```markdown
[docs](https://example.com)
```

### MD040 - Fenced Code Language

Fenced code blocks should name a language, or `text` when no language applies.

Bad:

````markdown
```
hello
```
````

Good:

````markdown
```text
hello
```
````

### MD041 - First Line Heading

The file should start with the configured heading level.

Bad:

```markdown
Intro paragraph
```

Good:

```markdown
# Document title
```

Default options:

```toml
[verification.rules.MD041]
level = 1
front_matter_title = "^\\s*title\\s*[:=]"
```

### MD046 - Code Block Style

Code blocks should match the configured style.

Bad with default `fenced`:

```markdown
    indented code
```

Good with default `fenced`:

````markdown
```text
fenced code
```
````

Default options:

```toml
[verification.rules.MD046]
style = "fenced"
```

Accepted styles are `fenced`, `indented`, and `consistent`.

### MD047 - Single Trailing Newline

Files should end with exactly one newline.

Bad:

```markdown
# Title
[EOF]
```

Good:

```markdown
# Title

[EOF marker not part of file]
```

### GFM001 - Table Delimiter

GFM table delimiter cells need at least three hyphens.

Bad:

```markdown
| A |
| - |
```

Good:

```markdown
| A |
| --- |
```

### GFM002 - Table Column Count

GFM table rows should match the header width.

Bad:

```markdown
| A | B |
| --- | --- |
| only one |
```

Good:

```markdown
| A | B |
| --- | --- |
| one | two |
```

### GFM003 - Task List Marker

Task list markers should contain a space or `x`.

Bad:

```markdown
- [y] almost done
```

Good:

```markdown
- [x] done
- [ ] pending
```

### MKF001 - Local Resource Exists

MkForge checks local image and link targets when a source path is available.
Remote URLs and fragment-only links are ignored.

Bad:

```markdown
![missing](missing.png)
```

Good:

```markdown
![present](present.png)
```
