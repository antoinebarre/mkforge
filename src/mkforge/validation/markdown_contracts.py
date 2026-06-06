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
from pathlib import Path

from mkforge.input_checks import require_bool, require_path, require_string
from mkforge.verification.policy import MarkdownSource
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
    require_string(markdown, "markdown", allow_empty=True)
    if not isinstance(expected, Mapping):
        kind = type(expected).__name__
        msg = f"expected YAML contract must be a mapping; got {kind}."
        raise TypeError(msg)
    require_bool(strict, "strict")

    actual = _parse_frontmatter(markdown)
    if actual is None:
        return False
    if strict and set(actual) != set(expected):
        return False
    return all(
        key in actual and _matches_expected_value(actual[key], value)
        for key, value in expected.items()
    )


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
    require_string(markdown, "markdown", allow_empty=True)
    _validate_string_sequence(expected, "expected chapters")
    require_bool(strict, "strict")

    actual = tuple(
        title
        for level, title in _heading_contracts(markdown)
        if level == _CHAPTER_LEVEL
    )
    required = tuple(expected)
    if strict:
        return actual == required
    return _is_ordered_subsequence(required, actual)


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
    require_string(markdown, "markdown", allow_empty=True)
    required = _validate_heading_contracts(expected)
    require_bool(strict, "strict")

    actual = _heading_contracts(markdown)
    if strict:
        return actual == required
    return _is_ordered_subsequence(required, actual)


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
    require_string(markdown, "markdown", allow_empty=True)
    root = _image_root(base_path)
    _validate_timeout(timeout)
    return all(
        _image_target_exists(target, root, timeout)
        for target in _image_targets(markdown)
    )


def _parse_frontmatter(markdown: str) -> dict[str, object] | None:
    """Parse a small MkForge-compatible YAML frontmatter block.

    Args:
        markdown: Markdown document text.

    Returns:
        Parsed flat frontmatter dictionary, or ``None`` when no valid
        frontmatter block exists.
    """
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    return _parse_yaml_lines(lines[1:end])


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


def _heading_contracts(markdown: str) -> tuple[tuple[int, str], ...]:
    """Return heading level and title contracts from Markdown in source order.

    Args:
        markdown: Markdown document text.

    Returns:
        Tuple of ``(level, title)`` pairs outside fenced code blocks.
    """
    source = MarkdownSource.from_text(markdown)
    headings: list[tuple[int, str]] = []
    for line in lines_outside_fenced_code(source):
        match = _ATX_HEADING.match(line.text)
        if match:
            headings.append(
                (len(match.group("mark")), match.group("body").strip()),
            )
    return tuple(headings)


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


def _image_targets(markdown: str) -> tuple[str, ...]:
    """Return Markdown image targets outside fenced code blocks.

    Args:
        markdown: Markdown document text.

    Returns:
        Tuple of raw image target paths or URLs.
    """
    source = MarkdownSource.from_text(markdown)
    targets: list[str] = []
    for line in lines_outside_fenced_code(source):
        targets.extend(
            _image_target(match.group("body"))
            for match in _IMAGE_REFERENCE.finditer(line.text)
        )
    return tuple(targets)


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


def _image_target_exists(target: str, root: Path, timeout: float) -> bool:
    """Return whether one image target exists locally or remotely.

    Args:
        target: Image path or URL.
        root: Local resolution root.
        timeout: Remote request timeout.

    Returns:
        True when the target exists.
    """
    if not target:
        return False
    if _is_remote_image(target):
        return _remote_image_exists(target, timeout)
    return (root / target).expanduser().exists()


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
