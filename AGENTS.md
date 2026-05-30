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

## Dependencies

- Minimize external dependencies.
- Prefer the Python standard library by default.
- Add third-party packages only when explicitly requested or when the standard
  library is clearly insufficient for the task.
- Before adding a dependency, document why it is needed.

## Design

- Keep public APIs narrow and stable.
- Avoid hidden side effects.
- Prefer pure functions for transformation logic.
- Validate inputs close to the boundary of the system.
- Make error messages precise and useful.

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
