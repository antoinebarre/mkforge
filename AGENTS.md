# Codex Instructions

These instructions apply to the whole repository.

## Coding Standards

- Write Python code that strictly follows Python PEP rules and the Google
  Python Style Guide.
- Keep each function small and focused.
- Keep cyclomatic complexity at or below 10 for every function.
- Keep Python modules below 500 lines unless an ADR explicitly justifies a
  larger module.
- Do not optimize for maintainability-index scores when they encourage
  artificial fragmentation into very small files.
- Write Google-style docstrings for every function and class, including private
  functions and classes.
- Prefer explicit, readable, auditable code over clever abstractions.
- Use clear names and simple control flow.
- Add comments only when they clarify non-obvious intent or constraints.
- Apply SOLID principles strictly:
  - Single Responsibility: each module, class, and function must have one clear
    reason to change.
  - Open/Closed: add behavior through new focused implementations, rules,
    strategies, or registries instead of editing large conditional blocks.
  - Liskov Substitution: implementations of a public protocol must remain
    interchangeable and must not weaken expected behavior.
  - Interface Segregation: depend on narrow protocols or callables rather than
    broad objects with unrelated responsibilities.
  - Dependency Inversion: high-level workflows depend on stable interfaces, not
    concrete low-level details.

## Dependencies

- Minimize external dependencies.
- Prefer the Python standard library by default.
- Add third-party packages only when explicitly requested or when the standard
  library is clearly insufficient for the task.
- Before adding a dependency, document why it is needed.

## Design

- Start substantial feature work and architecture changes with an Architecture
  Decision Record before implementing code.
- Include PlantUML diagrams in ADRs when they clarify structure, behavior,
  dependencies, lifecycles, or integration flows.
- Document the design patterns used in each ADR, including why each pattern is
  appropriate and what tradeoff it introduces.
- Define public APIs, internal interfaces, data contracts, and expected error
  behavior in the ADR before filling in feature implementation details.
- Implement features only after the architecture, API boundaries, and extension
  points are explicit enough to review.
- Prefer a clean package layout over compatibility with unpublished APIs.
- Name modules, classes, functions, variables, and tests with business/domain
  vocabulary first. Prefer names such as `verify_file`, `heading_slugs`, or
  `required_headings` over architecture-first names such as `node`, `leaf`,
  `manager`, `processor`, `handler`, `orchestrator`, or `service` unless those
  words are the real domain concept.
- Prefer concrete, short, auditable names over abstract framework names.
- Keep public APIs narrow and stable.
- Avoid hidden side effects.
- Prefer pure functions for transformation logic.
- Validate inputs close to the boundary of the system.
- Make error messages precise and useful.
- Use design patterns deliberately to improve maintainability and evolvability:
  - use Strategy when behavior varies by profile, format, rule, or policy;
  - use Registry when behavior must be extended without modifying the engine;
  - use Adapter when exposing a simple callable or external API behind an
    internal interface;
  - use Factory functions when object creation has validation or multiple
    variants;
  - use Template Method only when a workflow is stable and extension points are
    explicit.
- Do not introduce a design pattern for decoration. A pattern is acceptable only
  when it removes duplication, reduces conditional complexity, clarifies an
  extension point, or protects a public contract.
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
- Every module, function, class, method, and test must include a strict
  Google-style docstring, including private functions and classes.
- Function and method docstrings must include:
  - a precise summary that explains the domain behavior;
  - `Args:` for every parameter except `self` and `cls`;
  - `Returns:` for every non-`None` return value;
  - `Raises:` for every intentionally raised exception.
- Class docstrings must include `Attributes:` when instances expose public
  attributes.
- Module docstrings for diagnostic rules must explain what the rule checks, why
  it belongs to verification or validation, and what kind of diagnostic it
  emits.
- Avoid placeholder docstrings such as `Function result.`, vague summaries, or a
  single imperative sentence that does not document inputs and outputs.

## Quality Checks

Run these checks before considering code complete:

```bash
make check
```

Use `make ci` for non-mutating verification and `make check-dist` before
publishing.
