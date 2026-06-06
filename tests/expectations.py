"""Shared test expectation helpers."""


def expect(condition: object, detail: object) -> None:
    """Requirement: fail tests with explicit diagnostic detail."""
    if not condition:
        raise AssertionError(detail)
