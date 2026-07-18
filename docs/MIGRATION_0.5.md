# Migrating from 0.4.0 to 0.5.0

The four `validate_markdown_*` functions retain their signatures, boolean
results, and exceptions. No existing caller change is required.

Clients needing detail can replace `validate_markdown_yaml(...)` with
`diagnose_markdown_yaml(...)` (and likewise for headings, chapters, or images),
then use `report.passed`, `report.has_errors`, `report.has_warnings`, and iterate
`report.diagnostics`. Each diagnostic has a stable `rule_id`, source `line` and
`column`, human `message`, and optional structured `target`.
