"""Tests for structured Markdown contract diagnostics."""

# ruff: noqa: SLF001

import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import NoReturn, Self

import pytest

from mkforge import (
    Diagnostic,
    VerificationReport,
    diagnose_markdown_chapters,
    diagnose_markdown_headings,
    diagnose_markdown_images,
    diagnose_markdown_yaml,
)
from mkforge.validation import markdown_contracts


def test_diagnostics_reports_yaml_categories_and_positions() -> None:
    """Requirement: YAML diagnostics distinguish every contract violation."""
    cases = (
        ("# Report\n", "MKFYAML001"),
        ("---\ntitle: Report\n", "MKFYAML002"),
        ("---\n  bad: value\n---\n", "MKFYAML003"),
        ("---\ntitle: Report\n---\n", "MKFYAML004"),
    )
    for markdown, rule_id in cases:
        report = diagnose_markdown_yaml(markdown, {"draft": bool})
        if report.diagnostics[0].rule_id != rule_id:
            raise AssertionError(report)

    report = diagnose_markdown_yaml(
        "---\ntitle: Report\ndraft: no\nextra: yes\n---\n",
        {"title": "Other", "draft": bool, "missing": str},
        strict=True,
    )
    ids = {item.rule_id for item in report.diagnostics}
    if ids != {"MKFYAML004", "MKFYAML005", "MKFYAML006"}:
        raise AssertionError(report)
    if not report.has_errors or report.has_warnings or report.passed:
        raise AssertionError(report)


def test_diagnostics_reports_heading_and_chapter_categories() -> None:
    """Requirement: sequence diagnostics distinguish contract failures."""
    heading = diagnose_markdown_headings(
        "# B\n### A\n## Extra\n",
        ((2, "A"), (1, "B"), (2, "Missing")),
        strict=True,
    )
    ids = {item.rule_id for item in heading.diagnostics}
    if ids != {"MKFHEADING001", "MKFHEADING002", "MKFHEADING004"}:
        raise AssertionError(heading)
    ordered = diagnose_markdown_headings("# B\n# A\n", ((1, "A"), (1, "B")))
    if ordered.diagnostics[0].rule_id != "MKFHEADING003":
        raise AssertionError(ordered)

    chapter = diagnose_markdown_chapters(
        "## B\n## A\n## Extra\n",
        ("A", "B"),
        strict=True,
    )
    ids = {item.rule_id for item in chapter.diagnostics}
    if ids != {"MKFCHAPTER002", "MKFCHAPTER003"}:
        raise AssertionError(chapter)
    missing = diagnose_markdown_chapters("## A\n", ("Missing",))
    if missing.diagnostics[0].rule_id != "MKFCHAPTER001":
        raise AssertionError(missing)


def test_diagnostics_ignore_fences_and_return_empty_success() -> None:
    """Requirement: contract scans ignore fenced Markdown constructs."""
    markdown = "```\n# Hidden\n![Bad](missing.png)\n```\n## Visible\n"
    headings = diagnose_markdown_headings(markdown, ((2, "Visible"),))
    chapters = diagnose_markdown_chapters(markdown, ("Visible",))
    images = diagnose_markdown_images(markdown)
    for report in (headings, chapters, images):
        if not report.passed or report.diagnostics:
            raise AssertionError(report)


def test_report_severity_properties_are_independent() -> None:
    """Requirement: reports distinguish error and warning diagnostics."""
    warning = Diagnostic("TEST", "Test", 1, 1, "warning")
    report = VerificationReport("client", (warning,))
    if report.passed or report.has_errors or not report.has_warnings:
        raise AssertionError(report)


def test_image_diagnostics_cover_local_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: image diagnostics identify each invalid local target."""
    existing = tmp_path / "ok.png"
    existing.write_bytes(b"png")
    report = diagnose_markdown_images(
        "![Ok](ok.png)\n![Missing](missing.png)\n![Empty](   )\n",
        base_path=tmp_path / "document.md",
    )
    if [item.rule_id for item in report.diagnostics] != [
        "MKFIMAGE001",
        "MKFIMAGE001",
    ]:
        raise AssertionError(report)

    occurrence = markdown_contracts._Occurrence("denied.png", 2, 5)
    monkeypatch.setattr(Path, "exists", _raise_os_error)
    diagnostic = markdown_contracts._image_diagnostic(
        occurrence,
        tmp_path,
        1.0,
    )
    if diagnostic is None or diagnostic.rule_id != "MKFIMAGE002":
        raise AssertionError(diagnostic)


@pytest.mark.parametrize(
    ("failure", "rule_id"),
    [
        (markdown_contracts._RemoteFailure.MALFORMED, "MKFIMAGE003"),
        (markdown_contracts._RemoteFailure.UNREACHABLE, "MKFIMAGE004"),
        (markdown_contracts._RemoteFailure.HTTP, "MKFIMAGE005"),
        (markdown_contracts._RemoteFailure.NETWORK, "MKFIMAGE006"),
        (markdown_contracts._RemoteFailure.TIMEOUT, "MKFIMAGE007"),
    ],
)
def test_image_diagnostics_classify_remote_failures(
    failure: markdown_contracts._RemoteFailure,
    rule_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: remote image failures have distinct stable rule IDs."""
    monkeypatch.setattr(
        markdown_contracts,
        "_remote_failure",
        lambda _u, _t: failure,
    )
    report = diagnose_markdown_images("![Remote](https://example.com/a.png)\n")
    if report.diagnostics[0].rule_id != rule_id:
        raise AssertionError(report)


def test_remote_checks_cover_security_and_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: protected requests classify security and transport."""
    if markdown_contracts._remote_failure("https:///x.png", 1.0) is not (
        markdown_contracts._RemoteFailure.MALFORMED
    ):
        raise AssertionError(markdown_contracts._RemoteFailure.MALFORMED)
    monkeypatch.setattr(
        markdown_contracts,
        "_host_is_private",
        lambda _h: True,
    )
    if markdown_contracts._remote_failure(
        "https://private/x.png",
        1.0,
    ) is not (markdown_contracts._RemoteFailure.UNREACHABLE):
        raise AssertionError(markdown_contracts._RemoteFailure.UNREACHABLE)
    monkeypatch.setattr(
        markdown_contracts,
        "_host_is_private",
        lambda _h: False,
    )
    monkeypatch.setattr(
        markdown_contracts,
        "_request_failure",
        lambda _u, _m, _t: None,
    )
    if markdown_contracts._remote_failure("https://example.com/x.png", 1.0):
        raise AssertionError(markdown_contracts._RemoteFailure.NETWORK)
    failures = iter((markdown_contracts._RemoteFailure.NETWORK, None))
    monkeypatch.setattr(
        markdown_contracts,
        "_request_failure",
        lambda _u, _m, _t: next(failures),
    )
    if markdown_contracts._remote_failure("https://example.com/x.png", 1.0):
        raise AssertionError(markdown_contracts._RemoteFailure.NETWORK)


def test_internal_yaml_location_and_remote_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: parser locations and request success are deterministic."""
    if markdown_contracts._first_invalid_yaml_line(["", "  - item"]) != 0:
        raise AssertionError(markdown_contracts._first_invalid_yaml_line([]))
    monkeypatch.setattr(urllib.request, "urlopen", _open_ok)
    if markdown_contracts._request_failure(
        "https://example.com/x.png",
        "HEAD",
        1.0,
    ):
        raise AssertionError(markdown_contracts._RemoteFailure.NETWORK)


@pytest.mark.parametrize(
    ("opener_name", "expected"),
    [
        ("bad", markdown_contracts._RemoteFailure.HTTP),
        ("http", markdown_contracts._RemoteFailure.HTTP),
        ("timeout", markdown_contracts._RemoteFailure.TIMEOUT),
        ("network", markdown_contracts._RemoteFailure.NETWORK),
    ],
)
def test_request_failure_classifies_responses(
    opener_name: str,
    expected: markdown_contracts._RemoteFailure,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requirement: HTTP requests normalize response and exception failures."""
    openers = {
        "bad": _open_http_bad,
        "http": _open_http_error,
        "timeout": _open_timeout,
        "network": _open_network_error,
    }
    monkeypatch.setattr(urllib.request, "urlopen", openers[opener_name])
    actual = markdown_contracts._request_failure(
        "https://example.com/x.png",
        "HEAD",
        1.0,
    )
    if actual is not expected:
        raise AssertionError(actual)


def _raise_os_error(_path: Path) -> NoReturn:
    """Raise a deterministic local access error.

    Args:
        _path: Path instance receiving the call.

    Raises:
        OSError: Always raised.
    """
    raise OSError


class _Response:
    """Represent a fake HTTP response.

    Attributes:
        status: Fake HTTP status.
    """

    status = 500

    def __enter__(self) -> Self:
        """Return the active response.

        Returns:
            Fake response.
        """
        return self

    def __exit__(self, *args: object) -> None:
        """Leave the response context.

        Args:
            *args: Exception context values.
        """


def _open_http_bad(_request: object, *, timeout: float) -> _Response:
    """Return an invalid HTTP response.

    Args:
        _request: Request object.
        timeout: Request timeout.

    Returns:
        Fake invalid response.
    """
    if timeout <= 0:
        raise AssertionError(timeout)
    return _Response()


class _SuccessfulResponse(_Response):
    """Represent a successful fake HTTP response."""

    status = 200


def _open_ok(_request: object, *, timeout: float) -> _SuccessfulResponse:
    """Return a successful HTTP response.

    Args:
        _request: Request object.
        timeout: Request timeout.

    Returns:
        Fake successful response.
    """
    if timeout <= 0:
        raise AssertionError(timeout)
    return _SuccessfulResponse()


def _open_http_error(_request: object, *, timeout: float) -> NoReturn:
    """Raise an HTTP error.

    Args:
        _request: Request object.
        timeout: Request timeout.

    Raises:
        HTTPError: Always raised.
    """
    raise urllib.error.HTTPError(
        str(timeout),
        404,
        "missing",
        Message(),
        None,
    )


def _open_timeout(_request: object, *, timeout: float) -> NoReturn:
    """Raise a timeout.

    Args:
        _request: Request object.
        timeout: Request timeout.

    Raises:
        TimeoutError: Always raised.
    """
    raise TimeoutError(timeout)


def _open_network_error(_request: object, *, timeout: float) -> NoReturn:
    """Raise a network error.

    Args:
        _request: Request object.
        timeout: Request timeout.

    Raises:
        URLError: Always raised.
    """
    raise urllib.error.URLError(str(timeout))
