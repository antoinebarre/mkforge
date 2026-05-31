# Codex Instructions

These instructions apply to the whole repository.

## Coding Standards

- Write Python code that strictly follows Python PEP rules and the Google
  Python Style Guide.
- Keep each function small and focused.
- Keep cyclomatic complexity below 5 for every function.
- Keep maintainability above 85 when using maintainability metrics.
- Write Google-style docstrings for every function and class, including private
  functions and classes.
- Prefer explicit, readable, auditable code over clever abstractions.
- Use clear names and simple control flow.
- Add comments only when they clarify non-obvious intent or constraints.
- Apply SOLID principles: isolate responsibilities, depend on narrow
  interfaces, extend through explicit rules or registries, and avoid catch-all
  modules.

## Dependencies

- Minimize external dependencies.
- Prefer the Python standard library by default.
- Add third-party packages only when explicitly requested or when the standard
  library is clearly insufficient for the task.
- Before adding a dependency, document why it is needed.

## Design

- Prefer a clean package layout over compatibility with unpublished APIs.
- Prefer concrete, short names over abstract framework names.
- Keep public APIs narrow and stable.
- Avoid hidden side effects.
- Prefer pure functions for transformation logic.
- Validate inputs close to the boundary of the system.
- Make error messages precise and useful.
- Separate verification from validation:
  - verification checks Markdown or GitHub Flavored Markdown conformance;
  - validation checks document content, metadata, required headings, wording,
    and project-specific policies.
- Keep diagnostics auditable: one diagnostic rule must live in one Python
  module, grouped under the relevant `verification/` or `validation/`
  package, and the module docstring must explain precisely what the rule
  checks.
- Avoid Python files that only re-export imports. A module must own behavior,
  data, or documentation that justifies its existence.

## Tests and Documentation

- Maintain 100% test coverage.
- Write tests for all new behavior.
- Test function docstrings must state the requirement being verified.
- Every function and class must include a Google-style docstring, including
  private functions and classes.

## Quality Checks

Run these checks before considering code complete:

```bash
make check
```

Use `make ci` for non-mutating verification and `make check-dist` before
publishing.
