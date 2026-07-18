# ADR-003: Structured Markdown Contract Diagnostics

## Status

Accepted

## Context

The 0.4.0 Markdown contract helpers return booleans. Clients cannot aggregate
individual failures without parsing text or duplicating MkForge validation.
MkForge already exposes immutable `Diagnostic` values and
`VerificationReport`, so a second report model would fragment the public API.

## Decision

Add four `diagnose_markdown_*` functions beside the compatible `validate_*`
functions. A shared contract engine emits existing `Diagnostic` values with
stable `MKFYAMLxxx`, `MKFHEADINGxxx`, `MKFCHAPTERxxx`, and `MKFIMAGExxx` rule
identifiers, category `markdown-contract`, severity `error`, exact source
positions when available, and the offending key, title, path, or URL in the
new optional `Diagnostic.target` field.

The existing `VerificationReport(rule_set_name, diagnostics)` construction is
preserved. `passed` continues to mean that no diagnostic was emitted;
`has_errors` and `has_warnings` inspect severity independently. Contract
violations are errors, so all four meanings are unambiguous. Boolean helpers
delegate to the diagnostic APIs and return `.passed`.

Network checks retain the existing HTTP(S), DNS, private, loopback, and
link-local protections. An internal immutable result distinguishes malformed,
blocked/unreachable, HTTP, network, and timeout failures. No dependency is
added.

## Consequences

Clients can branch on stable rule IDs, severity, positions, and targets without
parsing messages. Existing constructors, boolean signatures, results, and
documented exceptions remain compatible. Adding the optional trailing
`Diagnostic.target` field is source compatible with positional and keyword
construction used in 0.4.0.

## Alternatives rejected

- A new validation-only report model would duplicate established concepts.
- Encoding targets in messages would force clients to parse human text.
- Replacing boolean helpers would break 0.4.0 clients.
- Adding a complete YAML package is unnecessary for MkForge's supported flat
  frontmatter subset.
