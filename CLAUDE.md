# Claude Code Instructions

These instructions apply to the whole repository.

## Coding Standards

- Strictly follow Python PEP rules and the Google Python Style Guide for all
  Python code.
- Keep each function's cyclomatic complexity at or below 10.
- Keep Python modules below 500 lines unless an ADR explicitly justifies a
  larger module.
- Do not split a module purely to reduce its line count or cyclomatic
  complexity. A split is justified only when the resulting modules have
  genuinely independent reasons to change. Validation helpers that are only
  ever used by one module belong in that module, not in a separate file.
- Do not optimize for maintainability-index scores when they encourage
  artificial fragmentation into very small files.
- Write Google-style docstrings for every function and class, including private
  functions and classes.
- Write clean, auditable code with simple control flow.
- Favor clarity over cleverness.
- Use precise names for modules, classes, functions, variables, and tests.
- Keep comments rare and useful.
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
- Prefer Python standard library packages.
- Do not add third-party dependencies unless explicitly requested by the user or
  unless there is a clear technical need that cannot reasonably be met with the
  standard library.
- Explain the reason for any new dependency before adding it.

## Implementation Guidance

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
- Keep changes focused on the requested behavior.
- Keep public interfaces small.
- Name modules, classes, functions, variables, and tests with business/domain
  vocabulary first. Prefer names such as `verify_file`, `heading_slugs`, or
  `required_headings` over architecture-first names such as `node`, `leaf`,
  `manager`, `processor`, `handler`, `orchestrator`, or `service` unless those
  words are the real domain concept.
- Prefer concrete, short, auditable names over abstract framework names.
- Avoid global mutable state unless there is a clear reason.
- Prefer deterministic behavior and explicit inputs.
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
- Keep diagnostics auditable: one diagnostic rule must live in one Python
  module, grouped under the relevant `verification/` or `validation/`
  package, and the module docstring must explain precisely what the rule
  checks.
- Avoid Python files that only re-export imports. A module must own behavior,
  data, or documentation that justifies its existence.
- Group code by business cohesion, not by technical layer. Content element
  types and their construction-time validation belong together. Rendering
  logic for all element types belongs in one rendering module. Do not create
  separate ``*_validation.py``, ``*_rendering.py``, or ``*_helpers.py``
  satellites when the behavior is inseparable from its host module.
- Write tests for new behavior.
- Maintain 100% test coverage.
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

Before finishing code changes, run:

```bash
make check
```

Use `make ci` for non-mutating verification and `make check-dist` before
publishing.
