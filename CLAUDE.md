# Claude Code Instructions

These instructions apply to the whole repository.

## Coding Standards

- Strictly follow Python PEP rules and the Google Python Style Guide for all
  Python code.
- Keep each function's cyclomatic complexity below 5.
- Keep maintainability above 85 when maintainability is measured.
- Write Google-style docstrings for every function and class, including private
  functions and classes.
- Write clean, auditable code with simple control flow.
- Favor clarity over cleverness.
- Use precise names for modules, classes, functions, variables, and tests.
- Keep comments rare and useful.

## Dependencies

- Minimize external dependencies.
- Prefer Python standard library packages.
- Do not add third-party dependencies unless explicitly requested by the user or
  unless there is a clear technical need that cannot reasonably be met with the
  standard library.
- Explain the reason for any new dependency before adding it.

## Implementation Guidance

- Keep changes focused on the requested behavior.
- Keep public interfaces small.
- Avoid global mutable state unless there is a clear reason.
- Prefer deterministic behavior and explicit inputs.
- Write tests for new behavior.
- Maintain 100% test coverage.
- Test function docstrings must state the requirement being verified.
- Every function and class must include a Google-style docstring, including
  private functions and classes.

## Quality Checks

Before finishing code changes, run:

```bash
make check
```

Use `make ci` for non-mutating verification and `make check-dist` before
publishing.
