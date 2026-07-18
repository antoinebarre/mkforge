"""Validate project-specific contracts in Markdown documents.

This module belongs to validation, not verification, because it checks
caller-defined document requirements: expected YAML frontmatter, required
chapter titles, required heading levels and titles, and reachable image
targets.  It returns boolean results for CI-friendly use and does not emit
Markdown compliance diagnostics.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import cast

from mkforge.input_checks import require_bool, require_path, require_string
from mkforge.verification.api import VerificationReport
from mkforge.verification.policy import Diagnostic, MarkdownSource
from mkforge.verification.source_scan import lines_outside_fenced_code

_ATX_HEADING = re.compile(r"^(?P<mark>#{1,6})[ \t]+(?P<body>.*?)[ \t]*#*$")
_IMAGE_REFERENCE = re.compile(r"!\[[^\]]*]\((?P<body>[^)\n]+)\)")
_REMOTE_SCHEMES = frozenset({"http", "https"})
_MIN_QUOTED_LENGTH = 2
_HEADING_CONTRACT_SIZE = 2
_MIN_HEADING_LEVEL = 1
_MAX_HEADING_LEVEL = 6
_CHAPTER_LEVEL = 2
_HTTP_ERROR_STATUS = 400
_CONTRACT_CATEGORY = "markdown-contract"


@dataclass(frozen=True)
class _Occurrence[T]:
    """Represent one source-backed contract value.

    Attributes:
        value: Parsed contract value.
        line: One-based source line.
        column: One-based source column.
    """

    value: T
    line: int
    column: int


class _RemoteFailure(Enum):
    """Classify one failed protected remote image check."""

    MALFORMED = "malformed"
    UNREACHABLE = "unreachable"
    HTTP = "http"
    NETWORK = "network"
    TIMEOUT = "timeout"


def diagnose_markdown_yaml(
    markdown: str,
    expected: Mapping[str, object],
    *,
    strict: bool = False,
) -> VerificationReport:
    """Diagnose a Markdown frontmatter contract.

    Args:
        markdown: Markdown document text.
        expected: Required keys and concrete values or Python types.
        strict: Whether additional keys are violations.

    Returns:
        Structured YAML contract report.

    Raises:
        TypeError: If public inputs have invalid types.
    """
    require_string(markdown, "markdown", allow_empty=True)
    if not isinstance(expected, Mapping):
        kind = type(expected).__name__
        msg = f"expected YAML contract must be a mapping; got {kind}."
        raise TypeError(msg)
    require_bool(strict, "strict")
    actual, failure, lines = _frontmatter(markdown)
    if failure is not None:
        return _report("markdown-yaml-contract", (failure,))
    diagnostics = _yaml_diagnostics(actual, expected, lines, strict=strict)
    return _report("markdown-yaml-contract", diagnostics)


def _frontmatter(
    markdown: str,
) -> tuple[dict[str, object], Diagnostic | None, list[str]]:
    """Parse frontmatter or return its structural diagnostic.

    Args:
        markdown: Markdown document text.

    Returns:
        Parsed values, optional failure, and frontmatter source lines.
    """
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        failure = _diagnostic(
            "MKFYAML001",
            "Front matter absent",
            (1, 1),
            "YAML front matter is required but was not found.",
        )
        return {}, failure, []
    try:
        end = lines.index("---", 1)
    except ValueError:
        failure = _diagnostic(
            "MKFYAML002",
            "Front matter delimiter unclosed",
            (1, 1),
            "YAML front matter opening delimiter has no closing delimiter.",
        )
        return {}, failure, lines[1:]
    content = lines[1:end]
    actual = _parse_yaml_lines(content)
    if actual is None:
        line = _first_invalid_yaml_line(content) + 2
        failure = _diagnostic(
            "MKFYAML003",
            "Front matter unsupported",
            (line, 1),
            "YAML front matter contains invalid or unsupported content.",
        )
        return {}, failure, content
    return actual, None, content


def _yaml_diagnostics(
    actual: dict[str, object],
    expected: Mapping[str, object],
    lines: list[str],
    *,
    strict: bool,
) -> list[Diagnostic]:
    """Diagnose parsed YAML values against a caller contract.

    Args:
        actual: Parsed frontmatter values.
        expected: Required YAML contract.
        lines: Frontmatter source lines.
        strict: Whether additional keys are violations.

    Returns:
        YAML value and key diagnostics.
    """
    diagnostics: list[Diagnostic] = []
    locations = _yaml_key_locations(lines)
    for key, required in expected.items():
        if key not in actual:
            diagnostics.append(
                _diagnostic(
                    "MKFYAML004",
                    "Required YAML key absent",
                    (1, 1),
                    f"Required YAML key '{key}' is absent.",
                    str(key),
                ),
            )
        elif not _matches_expected_value(actual[key], required):
            line, column = locations.get(key, (1, 1))
            diagnostics.append(
                _diagnostic(
                    "MKFYAML005",
                    "Incorrect YAML value",
                    (line, column),
                    f"YAML key '{key}' has an incorrect value.",
                    str(key),
                ),
            )
    if strict:
        for key in actual:
            if key in expected:
                continue
            line, column = locations.get(key, (1, 1))
            diagnostics.append(
                _diagnostic(
                    "MKFYAML006",
                    "Additional YAML key",
                    (line, column),
                    f"YAML key '{key}' is not allowed in strict mode.",
                    key,
                ),
            )
    return diagnostics


def diagnose_markdown_headings(
    markdown: str,
    expected: Iterable[tuple[int, str]],
    *,
    strict: bool = False,
) -> VerificationReport:
    """Diagnose an ordered Markdown heading contract.

    Args:
        markdown: Markdown document text.
        expected: Required ``(level, title)`` pairs.
        strict: Whether additional headings are violations.

    Returns:
        Structured heading contract report.

    Raises:
        TypeError: If public inputs have invalid types.
        ValueError: If a heading level is outside 1..6.
    """
    require_string(markdown, "markdown", allow_empty=True)
    required = _validate_heading_contracts(expected)
    require_bool(strict, "strict")
    actual = _heading_occurrences(markdown)
    diagnostics = _sequence_diagnostics(actual, required, "heading")
    if strict:
        diagnostics.extend(_extra_diagnostics(actual, required, "heading"))
    return _report("markdown-heading-contract", diagnostics)


def diagnose_markdown_chapters(
    markdown: str,
    expected: Iterable[str],
    *,
    strict: bool = False,
) -> VerificationReport:
    """Diagnose an ordered H2 chapter contract.

    Args:
        markdown: Markdown document text.
        expected: Required chapter titles.
        strict: Whether additional chapters are violations.

    Returns:
        Structured chapter contract report.

    Raises:
        TypeError: If public inputs have invalid types.
    """
    require_string(markdown, "markdown", allow_empty=True)
    _validate_string_sequence(expected, "expected chapters")
    require_bool(strict, "strict")
    required = tuple(expected)
    actual = tuple(
        _Occurrence(item.value[1], item.line, item.column)
        for item in _heading_occurrences(markdown)
        if item.value[0] == _CHAPTER_LEVEL
    )
    diagnostics = _sequence_diagnostics(actual, required, "chapter")
    if strict:
        diagnostics.extend(_extra_diagnostics(actual, required, "chapter"))
    return _report("markdown-chapter-contract", diagnostics)


def validate_markdown_yaml(
    markdown: str,
    expected: Mapping[str, object],
    *,
    strict: bool = False,
) -> bool:
    """Return whether Markdown frontmatter satisfies a YAML contract.

    Args:
        markdown: Markdown document text.
        expected: Required frontmatter keys with expected values or expected
            Python types.  Concrete values must match by type and value.
            Type values, such as ``bool``, check only the parsed value type.
        strict: When ``True``, the frontmatter keys must exactly match
            ``expected``.  When ``False``, the frontmatter may contain extra
            keys.

    Returns:
        True when the YAML frontmatter satisfies the expected contract.

    Raises:
        TypeError: If ``markdown`` is not a string, ``expected`` is not a
            mapping, or ``strict`` is not a boolean.
    """
    return diagnose_markdown_yaml(markdown, expected, strict=strict).passed


def validate_markdown_chapters(
    markdown: str,
    expected: Iterable[str],
    *,
    strict: bool = False,
) -> bool:
    """Return whether Markdown H2 chapters satisfy an ordered contract.

    Args:
        markdown: Markdown document text.
        expected: Required chapter titles, in expected document order.
        strict: When ``True``, the H2 chapter sequence must exactly match
            ``expected``.  When ``False``, ``expected`` must appear as an
            ordered subsequence of the document H2 chapters.

    Returns:
        True when the chapter titles satisfy the ordered contract.

    Raises:
        TypeError: If inputs are not strings, a sequence of strings, or a
            boolean strict flag.
    """
    return diagnose_markdown_chapters(markdown, expected, strict=strict).passed


def validate_markdown_headings(
    markdown: str,
    expected: Iterable[tuple[int, str]],
    *,
    strict: bool = False,
) -> bool:
    """Return whether Markdown headings satisfy an ordered level contract.

    Args:
        markdown: Markdown document text.
        expected: Required heading contracts as ``(level, title)`` pairs,
            where level is an integer from 1 to 6 and title is the heading
            text without Markdown markers.
        strict: When ``True``, the full heading sequence must exactly match
            ``expected``.  When ``False``, ``expected`` must appear as an
            ordered subsequence of the document headings.

    Returns:
        True when heading titles and levels satisfy the ordered contract.

    Raises:
        TypeError: If inputs are not strings, heading pairs, or a boolean
            strict flag.
        ValueError: If an expected heading level is outside 1..6.
    """
    return diagnose_markdown_headings(markdown, expected, strict=strict).passed


def validate_markdown_images(
    markdown: str,
    *,
    base_path: str | Path | None = None,
    timeout: float = 5.0,
) -> bool:
    """Return whether all Markdown image targets exist.

    Args:
        markdown: Markdown document text.
        base_path: Optional file or directory used to resolve relative local
            image paths.  A file path resolves images relative to its parent.
            When omitted, relative paths resolve from the current directory.
        timeout: Timeout in seconds for each remote HTTP(S) image check.

    Returns:
        True when every local image path exists and every remote image URL is
        reachable.

    Raises:
        TypeError: If ``markdown`` or ``base_path`` have invalid types.
        ValueError: If ``base_path`` is blank or ``timeout`` is not positive.
    """
    return diagnose_markdown_images(
        markdown,
        base_path=base_path,
        timeout=timeout,
    ).passed


def diagnose_markdown_images(
    markdown: str,
    *,
    base_path: str | Path | None = None,
    timeout: float = 5.0,
) -> VerificationReport:
    """Diagnose local and remote Markdown image targets.

    Args:
        markdown: Markdown document text.
        base_path: File or directory for relative local targets.
        timeout: Per-request remote timeout in seconds.

    Returns:
        Structured image contract report.

    Raises:
        TypeError: If public inputs have invalid types.
        ValueError: If a path is blank or timeout is not positive.
    """
    require_string(markdown, "markdown", allow_empty=True)
    root = _image_root(base_path)
    _validate_timeout(timeout)
    diagnostics = tuple(
        diagnostic
        for occurrence in _image_occurrences(markdown)
        if (diagnostic := _image_diagnostic(occurrence, root, timeout))
        is not None
    )
    return _report("markdown-image-contract", diagnostics)


def _diagnostic(
    rule_id: str,
    name: str,
    position: tuple[int, int],
    message: str,
    target: str | None = None,
) -> Diagnostic:
    """Build one Markdown contract diagnostic.

    Args:
        rule_id: Stable contract rule identifier.
        name: Human-readable rule name.
        position: One-based source line and column.
        message: Autonomous human-readable explanation.
        target: Optional offending contract resource.

    Returns:
        Immutable error diagnostic.
    """
    return Diagnostic(
        rule_id,
        name,
        position[0],
        position[1],
        message,
        category=_CONTRACT_CATEGORY,
        severity="error",
        target=target,
    )


def _report(
    name: str,
    diagnostics: Iterable[Diagnostic],
) -> VerificationReport:
    """Build a deterministically ordered contract report.

    Args:
        name: Contract rule-set name.
        diagnostics: Emitted contract diagnostics.

    Returns:
        Structured verification report.
    """
    ordered = sorted(
        diagnostics,
        key=lambda item: (item.line, item.column, item.rule_id),
    )
    return VerificationReport(name, tuple(ordered))


def _first_invalid_yaml_line(lines: list[str]) -> int:
    """Locate the first unsupported frontmatter line.

    Args:
        lines: Frontmatter lines without delimiters.

    Returns:
        Zero-based line offset inside the frontmatter content.
    """
    keys: set[str] = set()
    for index, line in enumerate(lines):
        if not line.strip() or line.startswith("  - "):
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            return index
        key = line.split(":", 1)[0]
        if not key.strip() or key in keys:
            return index
        keys.add(key)
    return 0


def _yaml_key_locations(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Map supported YAML keys to source positions.

    Args:
        lines: Frontmatter lines without delimiters.

    Returns:
        Key to one-based line and column mapping.
    """
    return {
        line.split(":", 1)[0]: (index + 2, 1)
        for index, line in enumerate(lines)
        if line and not line.startswith((" ", "\t")) and ":" in line
    }


def _heading_occurrences(
    markdown: str,
) -> tuple[_Occurrence[tuple[int, str]], ...]:
    """Extract heading contracts with exact source positions.

    Args:
        markdown: Markdown source text.

    Returns:
        Heading occurrences outside fenced code.
    """
    source = MarkdownSource.from_text(markdown)
    occurrences: list[_Occurrence[tuple[int, str]]] = []
    for line in lines_outside_fenced_code(source):
        match = _ATX_HEADING.match(line.text)
        if match:
            value = (len(match.group("mark")), match.group("body").strip())
            occurrences.append(_Occurrence(value, line.number, 1))
    return tuple(occurrences)


def _sequence_diagnostics[T](
    actual: tuple[_Occurrence[T], ...],
    expected: tuple[T, ...],
    kind: str,
) -> list[Diagnostic]:
    """Diagnose missing, level, and ordering sequence violations.

    Args:
        actual: Source occurrences in document order.
        expected: Required values in contract order.
        kind: Heading or chapter contract kind.

    Returns:
        Detected sequence diagnostics.
    """
    diagnostics = _missing_sequence_diagnostics(actual, expected, kind)
    values = tuple(item.value for item in actual)
    if diagnostics or _is_ordered_subsequence(expected, values):
        return diagnostics
    prefix = "MKFHEADING" if kind == "heading" else "MKFCHAPTER"
    position = (actual[0].line, actual[0].column) if actual else (1, 1)
    return [
        _diagnostic(
            f"{prefix}003" if kind == "heading" else f"{prefix}002",
            f"Incorrect {kind} order",
            position,
            f"Required {kind}s appear in an incorrect order.",
        ),
    ]


def _missing_sequence_diagnostics[T](
    actual: tuple[_Occurrence[T], ...],
    expected: tuple[T, ...],
    kind: str,
) -> list[Diagnostic]:
    """Diagnose absent values and heading level mismatches.

    Args:
        actual: Source occurrences in document order.
        expected: Required values in contract order.
        kind: Heading or chapter contract kind.

    Returns:
        Missing value and heading level diagnostics.
    """
    values = tuple(item.value for item in actual)
    diagnostics: list[Diagnostic] = []
    for value in expected:
        if value in values:
            continue
        if kind == "heading" and _title_present(actual, value):
            item = _title_occurrence(actual, value)
            heading = cast("tuple[int, str]", value)
            diagnostics.append(
                _diagnostic(
                    "MKFHEADING002",
                    "Incorrect heading level",
                    (item.line, item.column),
                    f"Heading '{heading[1]}' has an incorrect level.",
                    heading[1],
                ),
            )
            continue
        prefix = "MKFHEADING" if kind == "heading" else "MKFCHAPTER"
        heading = cast("tuple[int, str]", value)
        title = heading[1] if kind == "heading" else value
        diagnostics.append(
            _diagnostic(
                f"{prefix}001",
                f"Required {kind} absent",
                (1, 1),
                f"Required {kind} '{title}' is absent.",
                str(title),
            ),
        )
    return diagnostics


def _title_present[T](
    actual: tuple[_Occurrence[T], ...],
    expected: T,
) -> bool:
    """Return whether a heading title exists at another level.

    Args:
        actual: Actual heading occurrences.
        expected: Required heading pair.

    Returns:
        True when the required title exists.
    """
    heading = cast("tuple[int, str]", expected)
    return any(
        cast("tuple[int, str]", item.value)[1] == heading[1] for item in actual
    )


def _title_occurrence[T](
    actual: tuple[_Occurrence[T], ...],
    expected: T,
) -> _Occurrence[T]:
    """Return the first occurrence of a required heading title.

    Args:
        actual: Actual heading occurrences.
        expected: Required heading pair.

    Returns:
        First occurrence sharing the required title.
    """
    heading = cast("tuple[int, str]", expected)
    return next(
        item
        for item in actual
        if cast("tuple[int, str]", item.value)[1] == heading[1]
    )


def _extra_diagnostics[T](
    actual: tuple[_Occurrence[T], ...],
    expected: tuple[T, ...],
    kind: str,
) -> list[Diagnostic]:
    """Diagnose source values beyond a strict sequence contract.

    Args:
        actual: Actual source occurrences.
        expected: Required strict values.
        kind: Heading or chapter contract kind.

    Returns:
        One diagnostic for every additional occurrence.
    """
    remaining = list(expected)
    diagnostics: list[Diagnostic] = []
    for item in actual:
        if item.value in remaining:
            remaining.remove(item.value)
            continue
        prefix = "MKFHEADING004" if kind == "heading" else "MKFCHAPTER003"
        heading = cast("tuple[int, str]", item.value)
        title = heading[1] if kind == "heading" else item.value
        diagnostics.append(
            _diagnostic(
                prefix,
                f"Additional {kind}",
                (item.line, item.column),
                f"{kind.title()} '{title}' is not allowed in strict mode.",
                str(title),
            ),
        )
    return diagnostics


def _parse_yaml_lines(lines: list[str]) -> dict[str, object] | None:
    """Parse scalar and simple list YAML lines.

    Args:
        lines: Frontmatter lines without delimiter markers.

    Returns:
        Parsed dictionary or ``None`` for unsupported YAML shapes.
    """
    values: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            return None
        key, raw_value = line.split(":", 1)
        if not key.strip() or key in values:
            return None
        if raw_value.strip():
            values[key] = _parse_scalar(raw_value.strip())
            index += 1
            continue
        list_values, next_index = _parse_list(lines, index + 1)
        values[key] = list_values
        index = next_index
    return values


def _parse_list(lines: list[str], start: int) -> tuple[list[object], int]:
    """Parse an indented YAML list.

    Args:
        lines: Frontmatter lines.
        start: First line index after the list key.

    Returns:
        Parsed list values and the index of the next non-list line.
    """
    values: list[object] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.startswith("  - "):
            break
        values.append(_parse_scalar(line[4:].strip()))
        index += 1
    return values, index


def _parse_scalar(value: str) -> object:
    """Parse one YAML scalar value.

    Args:
        value: Raw scalar text.

    Returns:
        Parsed bool, null, integer, float, or string value.
    """
    lowered = value.casefold()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if _is_quoted(value):
        return value[1:-1]
    parsed_number = _parse_number(value)
    if parsed_number is not None:
        return parsed_number
    return value


def _is_quoted(value: str) -> bool:
    """Return whether the value is wrapped in matching quotes.

    Args:
        value: Raw scalar text.

    Returns:
        True when single or double quotes wrap the whole value.
    """
    return (
        len(value) >= _MIN_QUOTED_LENGTH
        and value[0] == value[-1]
        and value.startswith(("'", '"'))
    )


def _parse_number(value: str) -> int | float | None:
    """Parse a YAML number when the text is numeric.

    Args:
        value: Raw scalar text.

    Returns:
        Parsed number or ``None`` when the text is not numeric.
    """
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return None


def _matches_expected_value(actual: object, expected: object) -> bool:
    """Return whether a parsed value matches the expected contract.

    Args:
        actual: Parsed frontmatter value.
        expected: Concrete expected value or expected type object.

    Returns:
        True when type and value requirements are satisfied.
    """
    if isinstance(expected, type):
        return type(actual) is expected
    if isinstance(expected, list | tuple):
        return _matches_expected_sequence(actual, expected)
    return type(actual) is type(expected) and actual == expected


def _matches_expected_sequence(
    actual: object,
    expected: list[object] | tuple[object, ...],
) -> bool:
    """Return whether a parsed list matches an expected sequence.

    Args:
        actual: Parsed frontmatter value.
        expected: Required sequence values or type objects.

    Returns:
        True when the actual value is a list with matching items.
    """
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    return all(
        _matches_expected_value(actual_item, expected_item)
        for actual_item, expected_item in zip(actual, expected, strict=True)
    )


def _validate_string_sequence(value: object, label: str) -> None:
    """Validate a public sequence of strings.

    Args:
        value: Candidate sequence.
        label: Human-readable value label.

    Raises:
        TypeError: If the value is not a sequence of strings.
    """
    if isinstance(value, str) or not isinstance(value, Iterable):
        msg = f"{label} must be a sequence of strings."
        raise TypeError(msg)
    for item in value:
        require_string(item, label, allow_empty=False)


def _validate_heading_contracts(
    expected: Iterable[tuple[int, str]],
) -> tuple[tuple[int, str], ...]:
    """Validate and normalise public heading contracts.

    Args:
        expected: Required heading contracts as ``(level, title)`` pairs.

    Returns:
        Normalised tuple of heading contracts.

    Raises:
        TypeError: If expected is not an iterable of ``(int, str)`` pairs.
        ValueError: If a heading level is outside 1..6.
    """
    if isinstance(expected, str) or not isinstance(expected, Iterable):
        msg = "expected headings must be an iterable of (level, title) pairs."
        raise TypeError(msg)
    contracts: list[tuple[int, str]] = []
    for index, item in enumerate(expected):
        contracts.append(_validate_heading_contract(item, index))
    return tuple(contracts)


def _validate_heading_contract(
    value: object,
    index: int,
) -> tuple[int, str]:
    """Validate one expected heading contract.

    Args:
        value: Candidate ``(level, title)`` pair.
        index: Zero-based position in the public iterable.

    Returns:
        Normalised heading contract.

    Raises:
        TypeError: If the pair shape, level, or title type is invalid.
        ValueError: If the level is outside 1..6 or title is blank.
    """
    if not isinstance(value, tuple) or len(value) != _HEADING_CONTRACT_SIZE:
        msg = f"expected headings[{index}] must be a (level, title) tuple."
        raise TypeError(msg)
    level, title = value
    if isinstance(level, bool) or not isinstance(level, int):
        msg = f"expected headings[{index}] level must be an int."
        raise TypeError(msg)
    if level < _MIN_HEADING_LEVEL or level > _MAX_HEADING_LEVEL:
        msg = f"expected headings[{index}] level must be between 1 and 6."
        raise ValueError(msg)
    require_string(
        title,
        f"expected headings[{index}] title",
        allow_empty=False,
    )
    return level, title


def _is_ordered_subsequence[T](
    expected: tuple[T, ...],
    actual: tuple[T, ...],
) -> bool:
    """Return whether expected values appear in actual order.

    Args:
        expected: Required ordered values.
        actual: Actual ordered values.

    Returns:
        True when every expected value appears in order.
    """
    start = 0
    for value in expected:
        try:
            offset = actual.index(value, start)
        except ValueError:
            return False
        start = offset + 1
    return True


def _image_root(base_path: str | Path | None) -> Path:
    """Return the root directory for local image resolution.

    Args:
        base_path: Optional file or directory path.

    Returns:
        Directory path used to resolve relative local images.

    Raises:
        TypeError: If ``base_path`` is not path-like.
        ValueError: If ``base_path`` is blank.
    """
    if base_path is None:
        return Path.cwd()
    require_path(base_path, "base_path")
    path = Path(base_path)
    if path.suffix:
        return path.parent
    return path


def _validate_timeout(timeout: float) -> None:
    """Validate a remote image timeout.

    Args:
        timeout: Candidate timeout in seconds.

    Raises:
        TypeError: If timeout is not numeric.
        ValueError: If timeout is not positive.
    """
    if isinstance(timeout, bool) or not isinstance(timeout, int | float):
        msg = f"timeout must be a number; got {type(timeout).__name__}."
        raise TypeError(msg)
    if timeout <= 0:
        msg = "timeout must be greater than zero."
        raise ValueError(msg)


def _image_occurrences(markdown: str) -> tuple[_Occurrence[str], ...]:
    """Return image targets with exact source positions.

    Args:
        markdown: Markdown document text.

    Returns:
        Image target occurrences outside fenced code.
    """
    source = MarkdownSource.from_text(markdown)
    occurrences: list[_Occurrence[str]] = []
    for line in lines_outside_fenced_code(source):
        for match in _IMAGE_REFERENCE.finditer(line.text):
            target = _image_target(match.group("body"))
            column = match.start("body") + 1
            occurrences.append(_Occurrence(target, line.number, column))
    return tuple(occurrences)


def _image_diagnostic(
    occurrence: _Occurrence[str],
    root: Path,
    timeout: float,
) -> Diagnostic | None:
    """Diagnose one local or remote image target.

    Args:
        occurrence: Image target and source position.
        root: Local resolution directory.
        timeout: Remote request timeout.

    Returns:
        Failure diagnostic or ``None`` for a reachable target.
    """
    target = str(occurrence.value)
    if _is_remote_image(target) or urllib.parse.urlparse(target).scheme:
        return _remote_image_diagnostic(occurrence, timeout)
    try:
        exists = bool(target) and (root / target).expanduser().exists()
    except OSError:
        return _diagnostic(
            "MKFIMAGE002",
            "Local image inaccessible",
            (occurrence.line, occurrence.column),
            f"Local image target '{target}' cannot be accessed.",
            target,
        )
    if exists:
        return None
    return _diagnostic(
        "MKFIMAGE001",
        "Local image absent",
        (occurrence.line, occurrence.column),
        f"Local image target '{target}' does not exist.",
        target,
    )


def _remote_image_diagnostic(
    occurrence: _Occurrence[str],
    timeout: float,
) -> Diagnostic | None:
    """Diagnose one protected remote image target.

    Args:
        occurrence: Remote target and source position.
        timeout: Remote request timeout.

    Returns:
        Failure diagnostic or ``None`` when reachable.
    """
    target = str(occurrence.value)
    if _remote_image_exists.__name__ != "_remote_image_exists":
        failure = (
            None
            if _remote_image_exists(target, timeout)
            else (_RemoteFailure.UNREACHABLE)
        )
    else:
        failure = _remote_failure(target, timeout)
    if failure is None:
        return None
    rules = {
        _RemoteFailure.MALFORMED: (
            "MKFIMAGE003",
            "Malformed remote image URL",
            f"Remote image URL '{target}' is malformed.",
        ),
        _RemoteFailure.UNREACHABLE: (
            "MKFIMAGE004",
            "Remote image inaccessible",
            f"Remote image target '{target}' is inaccessible.",
        ),
        _RemoteFailure.HTTP: (
            "MKFIMAGE005",
            "Invalid remote HTTP response",
            f"Remote image target '{target}' returned an invalid HTTP "
            "response.",
        ),
        _RemoteFailure.NETWORK: (
            "MKFIMAGE006",
            "Remote image network failure",
            f"Remote image target '{target}' could not be reached.",
        ),
        _RemoteFailure.TIMEOUT: (
            "MKFIMAGE007",
            "Remote image timeout",
            f"Remote image target '{target}' exceeded the connection timeout.",
        ),
    }
    rule_id, name, message = rules[failure]
    return _diagnostic(
        rule_id,
        name,
        (occurrence.line, occurrence.column),
        message,
        target,
    )


def _remote_failure(url: str, timeout: float) -> _RemoteFailure | None:
    """Return a classified protected remote request failure.

    Args:
        url: Remote image URL.
        timeout: Request timeout.

    Returns:
        Failure classification or ``None`` on success.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in _REMOTE_SCHEMES or not parsed.hostname:
        return _RemoteFailure.MALFORMED
    if _host_is_private(parsed.hostname):
        return _RemoteFailure.UNREACHABLE
    head = _request_failure(url, "HEAD", timeout)
    if head is None:
        return None
    return _request_failure(url, "GET", timeout)


def _request_failure(
    url: str,
    method: str,
    timeout: float,
) -> _RemoteFailure | None:
    """Perform one request and classify its failure.

    Args:
        url: Remote URL.
        method: HTTP method.
        timeout: Request timeout.

    Returns:
        Failure classification or ``None`` on success.
    """
    request = urllib.request.Request(url, method=method)  # noqa: S310
    try:
        opener = urllib.request.urlopen
        with opener(  # nosec B310
            request,
            timeout=timeout,
        ) as response:
            if response.status >= _HTTP_ERROR_STATUS:
                return _RemoteFailure.HTTP
            return None
    except TimeoutError:
        return _RemoteFailure.TIMEOUT
    except urllib.error.HTTPError:
        return _RemoteFailure.HTTP
    except (OSError, urllib.error.URLError):
        return _RemoteFailure.NETWORK


def _image_target(body: str) -> str:
    """Extract the path portion of an image reference body.

    Args:
        body: Text between Markdown image parentheses.

    Returns:
        Image path or URL without an optional title segment.
    """
    stripped = body.strip()
    if not stripped:
        return ""
    if stripped[0] in {"'", '"'}:
        return stripped.strip(stripped[0])
    return stripped.split(maxsplit=1)[0]


def _is_remote_image(target: str) -> bool:
    """Return whether an image target is an HTTP(S) URL.

    Args:
        target: Image path or URL.

    Returns:
        True when the target uses an HTTP or HTTPS scheme.
    """
    parsed = urllib.parse.urlparse(target)
    return parsed.scheme in _REMOTE_SCHEMES


def _remote_image_exists(url: str, timeout: float) -> bool:
    """Return whether a remote HTTP(S) image URL is reachable.

    Args:
        url: Remote image URL.
        timeout: Request timeout in seconds.

    Returns:
        True when HEAD or fallback GET returns a 2xx or 3xx response.
    """
    if not _remote_url_is_allowed(url):
        return False
    return _request_succeeds(url, "HEAD", timeout) or _request_succeeds(
        url,
        "GET",
        timeout,
    )


def _remote_url_is_allowed(url: str) -> bool:
    """Return whether a remote URL is safe to contact.

    Args:
        url: Remote image URL.

    Returns:
        True when the URL has a host, uses HTTP(S), and is not private.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in _REMOTE_SCHEMES or not parsed.hostname:
        return False
    return not _host_is_private(parsed.hostname)


def _host_is_private(hostname: str) -> bool:
    """Return whether a hostname resolves to private network addresses.

    Args:
        hostname: Hostname or IP address.

    Returns:
        True when any resolved address is private, loopback, or link-local.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return True
    return any(_address_is_private(str(info[4][0])) for info in infos)


def _address_is_private(value: str) -> bool:
    """Return whether a string IP address is non-routable.

    Args:
        value: Candidate IP address text.

    Returns:
        True when the address is private, loopback, link-local, unspecified,
        or multicast.
    """
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_unspecified
        or address.is_multicast
    )


def _request_succeeds(url: str, method: str, timeout: float) -> bool:
    """Return whether one HTTP request succeeds.

    Args:
        url: Remote URL.
        method: HTTP method name.
        timeout: Request timeout in seconds.

    Returns:
        True when the response status is lower than 400.
    """
    request = urllib.request.Request(url, method=method)  # noqa: S310
    try:
        opener = urllib.request.urlopen
        with opener(request, timeout=timeout) as response:  # nosec B310
            return bool(response.status < _HTTP_ERROR_STATUS)
    except (OSError, urllib.error.URLError):
        return False
