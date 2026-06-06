"""Tests for project-specific Markdown validation contracts."""

# ruff: noqa: SLF001
# SLF001 is suppressed because these tests intentionally cover private parsing
# and URL helper branches that protect the public validation functions.

import socket
import urllib.request
from pathlib import Path
from typing import NoReturn, Self
from urllib.error import URLError

import pytest

from mkforge import (
    validate_markdown_chapters,
    validate_markdown_headings,
    validate_markdown_images,
    validate_markdown_yaml,
)
from mkforge.validation import markdown_contracts


def test_validation_yaml_accepts_minimum_expected_frontmatter() -> None:
    """Requirement: YAML validation accepts keys in non-strict mode."""
    markdown = (
        "---\n"
        "title: Release\n"
        "draft: false\n"
        "version: 3\n"
        "tags:\n"
        "  - docs\n"
        "  - api\n"
        "---\n\n"
        "# Release\n"
    )

    valid = validate_markdown_yaml(
        markdown,
        {"draft": False, "version": int, "tags": ["docs", str]},
    )

    if not valid:
        raise AssertionError(markdown)


def test_validation_yaml_rejects_strict_extra_keys_and_wrong_types() -> None:
    """Requirement: YAML validation checks strict keys and value formats."""
    markdown = "---\ntitle: Release\ndraft: false\n---\n\n# Release\n"

    if validate_markdown_yaml(markdown, {"draft": False}, strict=True):
        raise AssertionError(markdown)
    if validate_markdown_yaml(markdown, {"draft": "false"}):
        raise AssertionError(markdown)
    if validate_markdown_yaml("# Missing\n", {"draft": bool}):
        raise AssertionError(markdown)


def test_validation_chapters_accepts_ordered_minimum_sequence() -> None:
    """Requirement: chapter validation accepts ordered required chapters."""
    markdown = (
        "# Report\n\n## Context\n\n### Detail\n\n## Architecture\n\n## Tests\n"
    )

    valid = validate_markdown_chapters(markdown, ("Context", "Tests"))

    if not valid:
        raise AssertionError(markdown)


def test_validation_chapters_rejects_wrong_order_and_strict_mismatch() -> None:
    """Requirement: chapter validation enforces order and strict equality."""
    markdown = "# Report\n\n## Context\n\n## Architecture\n\n## Tests\n"

    if validate_markdown_chapters(markdown, ("Tests", "Context")):
        raise AssertionError(markdown)
    if validate_markdown_chapters(
        markdown,
        ("Context", "Tests"),
        strict=True,
    ):
        raise AssertionError(markdown)


def test_validation_headings_accepts_ordered_level_contract() -> None:
    """Requirement: heading validation checks title order and levels."""
    markdown = (
        "# Report\n\n"
        "## Context\n\n"
        "### Architecture\n\n"
        "### Tests\n\n"
        "## Conclusion\n"
    )

    valid = validate_markdown_headings(
        markdown,
        ((2, "Context"), (3, "Tests"), (2, "Conclusion")),
    )

    if not valid:
        raise AssertionError(markdown)


def test_validation_headings_rejects_wrong_level_and_order() -> None:
    """Requirement: heading validation rejects wrong levels and order."""
    markdown = "# Report\n\n## Context\n\n### Architecture\n\n### Tests\n"

    if validate_markdown_headings(markdown, ((3, "Context"),)):
        raise AssertionError(markdown)
    if validate_markdown_headings(
        markdown,
        ((3, "Tests"), (2, "Context")),
    ):
        raise AssertionError(markdown)


def test_validation_headings_enforces_strict_full_sequence() -> None:
    """Requirement: strict heading validation checks the full sequence."""
    markdown = "# Report\n\n## Context\n\n### Tests\n"

    if not validate_markdown_headings(
        markdown,
        ((1, "Report"), (2, "Context"), (3, "Tests")),
        strict=True,
    ):
        raise AssertionError(markdown)
    if validate_markdown_headings(
        markdown,
        ((2, "Context"), (3, "Tests")),
        strict=True,
    ):
        raise AssertionError(markdown)


def test_validation_images_accepts_existing_local_and_remote_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: image validation checks local files and remote URLs."""
    image = tmp_path / "chart.png"
    image.write_bytes(b"png")
    markdown = (
        "# Report\n\n"
        "![Local](chart.png)\n\n"
        "![Remote](https://example.com/chart.png)\n"
    )

    monkeypatch.setattr(markdown_contracts, "_remote_image_exists", _url_ok)

    if not validate_markdown_images(markdown, base_path=tmp_path / "doc.md"):
        raise AssertionError(markdown)


def test_validation_images_rejects_missing_local_and_remote_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: image validation fails when any image target is missing."""
    local_markdown = "# Report\n\n![Missing](missing.png)\n"
    remote_markdown = (
        "# Report\n\n![Missing](https://example.com/missing.png)\n"
    )

    monkeypatch.setattr(markdown_contracts, "_remote_image_exists", _url_bad)

    if validate_markdown_images(local_markdown, base_path=tmp_path):
        raise AssertionError(local_markdown)
    if validate_markdown_images(remote_markdown):
        raise AssertionError(remote_markdown)


def test_validation_public_inputs_fail_fast() -> None:
    """Requirement: validation APIs reject invalid public inputs."""
    with pytest.raises(TypeError, match="markdown must be a string"):
        validate_markdown_yaml(1, {})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="expected YAML contract"):
        validate_markdown_yaml("", [])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="expected chapters"):
        validate_markdown_chapters("", "Intro")
    with pytest.raises(TypeError, match="expected headings"):
        validate_markdown_headings("", "Intro")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"expected headings\[0\]"):
        validate_markdown_headings("", ["Intro"])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="level must be an int"):
        validate_markdown_headings("", [(True, "Intro")])
    with pytest.raises(ValueError, match="between 1 and 6"):
        validate_markdown_headings("", [(7, "Intro")])
    with pytest.raises(ValueError, match="title cannot be empty"):
        validate_markdown_headings("", [(2, " ")])
    with pytest.raises(ValueError, match="base_path cannot be empty"):
        validate_markdown_images("", base_path="")
    with pytest.raises(TypeError, match="timeout must be a number"):
        validate_markdown_images("", timeout=True)
    with pytest.raises(ValueError, match="timeout must be greater than zero"):
        validate_markdown_images("", timeout=0)


def test_validation_yaml_rejects_unsupported_frontmatter_shapes() -> None:
    """Requirement: YAML validation rejects unsupported frontmatter shapes."""
    invalid_sources = (
        "---\ntitle: Release\n",
        "---\n  title: Release\n---\n",
        "---\ntitle\n---\n",
        "---\n: missing\n---\n",
        "---\ntitle: One\ntitle: Two\n---\n",
    )

    for markdown in invalid_sources:
        if validate_markdown_yaml(markdown, {"title": str}):
            raise AssertionError(markdown)


def test_validation_yaml_accepts_scalar_formats() -> None:
    """Requirement: YAML validation parses supported scalar formats."""
    markdown = (
        "---\n"
        "\n"
        "published: true\n"
        "archived: null\n"
        "ratio: 1.5\n"
        "quoted: 'true'\n"
        "tags:\n"
        "  - docs\n"
        "status: stable\n"
        "---\n"
    )

    valid = validate_markdown_yaml(
        markdown,
        {
            "published": True,
            "archived": None,
            "ratio": 1.5,
            "quoted": "true",
            "tags": ["docs"],
            "status": "stable",
        },
    )

    if not valid:
        raise AssertionError(markdown)
    if validate_markdown_yaml(markdown, {"tags": ["docs", "api"]}):
        raise AssertionError(markdown)


def test_validation_images_ignores_fenced_code_and_rejects_empty_target(
    tmp_path: Path,
) -> None:
    """Requirement: image validation scans images outside fenced code only."""
    image = tmp_path / "ok.png"
    image.write_bytes(b"png")
    fenced = "```\n![Missing](missing.png)\n```\n\n![Ok](ok.png)\n"
    empty = "# Report\n\n![Empty](   )\n"

    if not validate_markdown_images(fenced, base_path=tmp_path):
        raise AssertionError(fenced)
    if validate_markdown_images(empty, base_path=tmp_path):
        raise AssertionError(empty)


def test_validation_images_accepts_quoted_local_targets(
    tmp_path: Path,
) -> None:
    """Requirement: image validation resolves quoted local image targets."""
    image = tmp_path / "chart file.png"
    image.write_bytes(b"png")
    markdown = '# Report\n\n![Chart]("chart file.png")\n'

    if not validate_markdown_images(markdown, base_path=tmp_path):
        raise AssertionError(markdown)


def test_validation_url_helpers_cover_allowed_and_private_hosts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: remote image validation rejects unsafe URL targets."""
    private_info = [(None, None, None, None, ("127.0.0.1", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", _raise_gai)
    if not markdown_contracts._host_is_private("missing.example"):
        _fail("DNS failures must be treated as private")

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda _host, _port: private_info,
    )
    if not markdown_contracts._host_is_private("localhost"):
        _fail("loopback hosts must be private")
    if markdown_contracts._remote_url_is_allowed("ftp://example.com/a.png"):
        _fail("non-HTTP URL allowed")
    if markdown_contracts._remote_url_is_allowed("https:///a.png"):
        _fail("hostless URL allowed")
    if markdown_contracts._remote_image_exists("https://localhost/a.png", 1.0):
        _fail("private remote image allowed")
    if markdown_contracts._address_is_private("example.com"):
        _fail("hostnames must not be parsed as private IP addresses")


def test_validation_remote_requests_use_head_then_get(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: remote image validation uses HEAD with GET fallback."""
    calls: list[str] = []

    def _fake_request_succeeds(
        url: str,
        method: str,
        timeout: float,
    ) -> bool:
        """Return success only for GET requests.

        Args:
            url: Remote image URL.
            method: HTTP method.
            timeout: Request timeout.

        Returns:
            True only for GET.
        """
        calls.append(f"{method}:{url}:{timeout}")
        return method == "GET"

    monkeypatch.setattr(
        markdown_contracts,
        "_remote_url_is_allowed",
        _allow_url,
    )
    monkeypatch.setattr(
        markdown_contracts,
        "_request_succeeds",
        _fake_request_succeeds,
    )

    if not markdown_contracts._remote_image_exists(
        "https://example.com/a.png",
        2.0,
    ):
        raise AssertionError(calls)
    if calls != [
        "HEAD:https://example.com/a.png:2.0",
        "GET:https://example.com/a.png:2.0",
    ]:
        raise AssertionError(calls)


def test_validation_request_helper_handles_success_and_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: low-level remote requests return boolean results."""
    monkeypatch.setattr(urllib.request, "urlopen", _open_ok)

    if not markdown_contracts._request_succeeds(
        "https://example.com/a.png",
        "HEAD",
        1.0,
    ):
        _fail("expected request success")

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        _open_bad,
    )
    if markdown_contracts._request_succeeds(
        "https://example.com/a.png",
        "HEAD",
        1.0,
    ):
        _fail("expected request failure")


def _url_ok(url: str, timeout: float) -> bool:
    """Return a successful fake URL existence result.

    Args:
        url: Remote image URL.
        timeout: Request timeout in seconds.

    Returns:
        Always True for deterministic tests.
    """
    return bool(url and timeout)


def _url_bad(url: str, timeout: float) -> bool:
    """Return a failed fake URL existence result.

    Args:
        url: Remote image URL.
        timeout: Request timeout in seconds.

    Returns:
        Always False for deterministic tests.
    """
    return bool(not url and timeout)


def _allow_url(url: str) -> bool:
    """Return whether a fake URL is allowed.

    Args:
        url: Candidate URL.

    Returns:
        True when the URL is not empty.
    """
    return bool(url)


def _raise_gai(hostname: str, port: object) -> NoReturn:
    """Raise a deterministic DNS error for host checks.

    Args:
        hostname: Hostname passed by the caller.
        port: Port passed by the caller.

    Raises:
        socket.gaierror: Always raised for deterministic tests.
    """
    raise socket.gaierror(hostname, port)


def _fail(message: str) -> NoReturn:
    """Raise an assertion error with a dynamic message.

    Args:
        message: Failure message.

    Raises:
        AssertionError: Always raised with the supplied message.
    """
    raise AssertionError(message)


class _FakeResponse:
    """Small context manager that mimics an HTTP response.

    Attributes:
        status: HTTP status code exposed by urllib responses.
    """

    status = 200

    def __enter__(self) -> Self:
        """Enter the fake response context.

        Returns:
            The fake response instance.
        """
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        """Exit the fake response context.

        Args:
            exc_type: Exception type raised inside the context, if any.
            exc_value: Exception instance raised inside the context, if any.
            traceback: Traceback raised inside the context, if any.
        """


def _open_ok(request: object, timeout: float) -> _FakeResponse:
    """Return a successful fake response.

    Args:
        request: urllib request object.
        timeout: Request timeout.

    Returns:
        Fake response with a success status.
    """
    if not request or not timeout:
        _fail("request and timeout are required")
    return _FakeResponse()


def _open_bad(request: object, timeout: float) -> _FakeResponse:
    """Raise a deterministic URL error.

    Args:
        request: urllib request object.
        timeout: Request timeout.

    Raises:
        URLError: Always raised for deterministic tests.
    """
    if not request or not timeout:
        _fail("request and timeout are required")
    msg = "offline"
    raise URLError(msg)
