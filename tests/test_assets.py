"""Tests for asset collection, verification, copy, and path rewriting."""

from __future__ import annotations

import ipaddress
import warnings
from pathlib import Path
from tempfile import gettempdir
from unittest.mock import patch
from urllib.error import URLError

import pytest

from mkforge import (
    Chapter,
    DownloadAssetError,
    Image,
    MissingAssetError,
    Report,
    Section,
)
from mkforge.assets import (
    _fetch_url,
    _is_private_host,
    collect_local_image_paths,
    collect_remote_image_urls,
    copy_assets_to_dir,
    download_assets_to_dir,
    rewrite_image_paths,
    verify_assets,
)

# ---------------------------------------------------------------------------
# collect_local_image_paths
# ---------------------------------------------------------------------------


def test_collect_skips_remote_urls() -> None:
    """Requirement: scheme, protocol-relative, and www paths are excluded."""
    remote_paths = [
        "https://example.com/img.png",
        "http://example.com/img.png",
        "ftp://example.com/img.png",
        "//cdn.example.com/img.png",
        "www.example.com/img.png",
    ]
    for remote in remote_paths:
        report = Report("R").add(Chapter("C").add(Image(remote, alt="r")))
        result = collect_local_image_paths(report)
        if result:
            msg = f"{remote!r} was not classified as remote"
            raise AssertionError(msg)


def test_collect_returns_resolved_local_paths(tmp_path: Path) -> None:
    """Requirement: local paths are returned resolved to absolute paths."""
    img = tmp_path / "chart.png"
    img.write_bytes(b"")
    report = Report("R").add(Chapter("C").add(Image(str(img), alt="chart")))
    result = collect_local_image_paths(report)
    if result != [img.resolve()]:
        raise AssertionError(result)


def test_collect_walks_nested_sections(tmp_path: Path) -> None:
    """Requirement: images inside nested sections are collected."""
    img = tmp_path / "deep.png"
    img.write_bytes(b"")
    report = Report("R").add(
        Chapter("C").add(
            Section("S").add(Image(str(img), alt="deep")),
        ),
    )
    result = collect_local_image_paths(report)
    if result != [img.resolve()]:
        raise AssertionError(result)


def test_collect_returns_empty_for_non_report() -> None:
    """Requirement: non-Report objects return an empty list without error."""
    result = collect_local_image_paths(object())
    if result:
        raise AssertionError(result)


# ---------------------------------------------------------------------------
# verify_assets
# ---------------------------------------------------------------------------


def test_verify_passes_when_all_paths_exist(tmp_path: Path) -> None:
    """Requirement: verify_assets succeeds when every path exists."""
    img = tmp_path / "ok.png"
    img.write_bytes(b"")
    verify_assets([img])  # must not raise


def test_verify_raises_missing_asset_error_for_absent_path(
    tmp_path: Path,
) -> None:
    """Requirement: MissingAssetError is raised listing missing paths."""
    missing = tmp_path / "ghost.png"
    with pytest.raises(MissingAssetError) as exc_info:
        verify_assets([missing])
    if missing not in exc_info.value.missing:
        raise AssertionError(exc_info.value.missing)


def test_verify_empty_list_passes() -> None:
    """Requirement: verify_assets with no paths succeeds."""
    verify_assets([])  # must not raise


def test_missing_asset_error_message_contains_path(tmp_path: Path) -> None:
    """Requirement: MissingAssetError message includes the missing path."""
    missing = tmp_path / "missing.png"
    error = MissingAssetError([missing])
    if str(missing) not in str(error):
        raise AssertionError(str(error))


# ---------------------------------------------------------------------------
# copy_assets_to_dir
# ---------------------------------------------------------------------------


def test_copy_places_file_in_assets_dir(tmp_path: Path) -> None:
    """Requirement: copy_assets_to_dir writes the file to assets_dir."""
    src = tmp_path / "chart.png"
    src.write_bytes(b"PNG")
    assets_dir = tmp_path / "assets"
    path_map = copy_assets_to_dir([src], assets_dir)
    if not (assets_dir / "chart.png").exists():
        msg = "file not copied"
        raise AssertionError(msg)
    if path_map[src] != "assets/chart.png":
        raise AssertionError(path_map)


def test_copy_renames_colliding_files_and_warns(tmp_path: Path) -> None:
    """Requirement: colliding filenames are renamed with a warning."""
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    img_a = dir_a / "chart.png"
    img_b = dir_b / "chart.png"
    img_a.write_bytes(b"A")
    img_b.write_bytes(b"B")
    assets_dir = tmp_path / "assets"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        path_map = copy_assets_to_dir([img_a, img_b], assets_dir)
    renamed = set(path_map.values())
    if "assets/chart.png" not in renamed:
        raise AssertionError(path_map)
    if "assets/chart_1.png" not in renamed:
        raise AssertionError(path_map)
    if not any("renamed" in str(w.message).lower() for w in caught):
        msg = "no warning emitted for collision"
        raise AssertionError(msg)


def test_copy_skips_duplicate_paths(tmp_path: Path) -> None:
    """Requirement: the same resolved path is copied only once."""
    src = tmp_path / "img.png"
    src.write_bytes(b"PNG")
    assets_dir = tmp_path / "assets"
    path_map = copy_assets_to_dir([src, src], assets_dir)
    if len(path_map) != 1:
        raise AssertionError(path_map)


# ---------------------------------------------------------------------------
# rewrite_image_paths
# ---------------------------------------------------------------------------


def test_rewrite_replaces_original_path_with_assets_relative() -> None:
    """Requirement: rewrite_image_paths substitutes resolved paths."""
    src = (Path(gettempdir()) / "project" / "chart.png").resolve()
    path_map = {src: "assets/chart.png"}
    markdown = f"![fig]({src})"
    result = rewrite_image_paths(markdown, path_map)
    if "assets/chart.png" not in result:
        raise AssertionError(result)


def test_rewrite_returns_unchanged_markdown_for_empty_map() -> None:
    """Requirement: rewrite_image_paths is a no-op with an empty map."""
    markdown = "![fig](chart.png)"
    result = rewrite_image_paths(markdown, {})
    if result != markdown:
        raise AssertionError(result)


# ---------------------------------------------------------------------------
# Integration: save with copy_assets
# ---------------------------------------------------------------------------


def test_save_raises_missing_asset_error_before_writing(
    tmp_path: Path,
) -> None:
    """Requirement: save() raises MissingAssetError if an image is absent."""
    output = tmp_path / "report.md"
    report = Report("R").add(
        Chapter("C").add(Image(str(tmp_path / "ghost.png"), alt="missing")),
    )
    with pytest.raises(MissingAssetError):
        report.save(output)
    if output.exists():
        msg = "output written despite missing asset"
        raise AssertionError(msg)


def test_save_writes_report_when_no_local_images(tmp_path: Path) -> None:
    """Requirement: save() succeeds when no local images are referenced."""
    output = tmp_path / "report.md"
    report = Report("R").add(Chapter("C"))
    report.save(output)
    if not output.exists():
        msg = "output not written"
        raise AssertionError(msg)


def test_save_copy_assets_rewrites_links(tmp_path: Path) -> None:
    """Requirement: copy_assets=True copies image and rewrites link."""
    img = tmp_path / "chart.png"
    img.write_bytes(b"PNG")
    output = tmp_path / "report.md"
    report = Report("R").add(
        Chapter("C").add(Image(str(img), alt="chart")),
    )
    report.save(output, copy_assets=True)
    content = output.read_text(encoding="utf-8")
    if "assets/chart.png" not in content:
        raise AssertionError(content)
    if not (tmp_path / "assets" / "chart.png").exists():
        msg = "asset not copied"
        raise AssertionError(msg)


def test_save_no_copy_preserves_original_link(tmp_path: Path) -> None:
    """Requirement: copy_assets=False writes original paths unchanged."""
    img = tmp_path / "chart.png"
    img.write_bytes(b"PNG")
    output = tmp_path / "report.md"
    report = Report("R").add(
        Chapter("C").add(Image(str(img), alt="chart")),
    )
    report.save(output, copy_assets=False)
    content = output.read_text(encoding="utf-8")
    if str(img) not in content:
        raise AssertionError(content)


# ---------------------------------------------------------------------------
# collect_remote_image_urls
# ---------------------------------------------------------------------------


def test_collect_remote_urls_returns_remote_paths() -> None:
    """Requirement: remote image URLs are collected from the report tree."""
    urls = [
        "https://example.com/img.png",
        "http://example.com/img.png",
        "ftp://files.example.com/img.png",
        "//cdn.example.com/img.png",
        "www.example.com/img.png",
    ]
    for url in urls:
        report = Report("R").add(Chapter("C").add(Image(url, alt="r")))
        result = collect_remote_image_urls(report)
        if result != [url]:
            msg = f"{url!r} not collected as remote: {result}"
            raise AssertionError(msg)


def test_collect_remote_skips_local_paths(tmp_path: Path) -> None:
    """Requirement: local image paths are excluded from remote collection."""
    img = tmp_path / "chart.png"
    img.write_bytes(b"")
    report = Report("R").add(Chapter("C").add(Image(str(img), alt="local")))
    result = collect_remote_image_urls(report)
    if result:
        raise AssertionError(result)


def test_collect_remote_returns_empty_for_non_report() -> None:
    """Requirement: non-Report objects return an empty list without error."""
    result = collect_remote_image_urls(object())
    if result:
        raise AssertionError(result)


def test_collect_remote_walks_nested_sections() -> None:
    """Requirement: remote images inside nested sections are collected."""
    url = "https://example.com/deep.png"
    report = Report("R").add(
        Chapter("C").add(Section("S").add(Image(url, alt="deep"))),
    )
    result = collect_remote_image_urls(report)
    if result != [url]:
        raise AssertionError(result)


# ---------------------------------------------------------------------------
# download_assets_to_dir
# ---------------------------------------------------------------------------


def _write_bytes(_url: str, dest: str) -> None:
    """Write dummy bytes to dest, simulating urlretrieve.

    Args:
        _url: Ignored URL argument (required by urlretrieve signature).
        dest: Destination file path to write.
    """
    Path(dest).write_bytes(b"PNG")


def test_download_writes_file_to_assets_dir(tmp_path: Path) -> None:
    """Requirement: downloaded file is written into assets_dir."""
    assets_dir = tmp_path / "assets"
    url = "https://example.com/chart.png"
    dest = assets_dir / "chart.png"
    with patch("urllib.request.urlretrieve", side_effect=_write_bytes):
        url_map = download_assets_to_dir([url], assets_dir)
    if url_map[url] != "assets/chart.png":
        raise AssertionError(url_map)
    if not dest.exists():
        msg = "file not written"
        raise AssertionError(msg)


def test_download_raises_download_asset_error_on_failure(
    tmp_path: Path,
) -> None:
    """Requirement: DownloadAssetError is raised when download fails."""
    assets_dir = tmp_path / "assets"
    url = "https://example.com/missing.png"
    with (
        patch("urllib.request.urlretrieve", side_effect=URLError("timeout")),
        pytest.raises(DownloadAssetError) as exc_info,
    ):
        download_assets_to_dir([url], assets_dir)
    if exc_info.value.url != url:
        raise AssertionError(exc_info.value)


def test_download_skips_duplicate_urls(tmp_path: Path) -> None:
    """Requirement: the same URL is downloaded only once."""
    assets_dir = tmp_path / "assets"
    url = "https://example.com/img.png"
    with patch(
        "urllib.request.urlretrieve",
        side_effect=_write_bytes,
    ) as mock_dl:
        url_map = download_assets_to_dir([url, url], assets_dir)
    if len(url_map) != 1:
        raise AssertionError(url_map)
    if mock_dl.call_count != 1:
        raise AssertionError(mock_dl.call_count)


def test_download_renames_colliding_filenames(tmp_path: Path) -> None:
    """Requirement: colliding filenames from different URLs are renamed."""
    assets_dir = tmp_path / "assets"
    url_a = "https://a.com/chart.png"
    url_b = "https://b.com/chart.png"
    with (
        patch("urllib.request.urlretrieve", side_effect=_write_bytes),
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("always")
        url_map = download_assets_to_dir([url_a, url_b], assets_dir)
    renamed = set(url_map.values())
    if "assets/chart.png" not in renamed:
        raise AssertionError(url_map)
    if "assets/chart_1.png" not in renamed:
        raise AssertionError(url_map)
    if not any("renamed" in str(w.message).lower() for w in caught):
        msg = "no warning emitted for collision"
        raise AssertionError(msg)


def test_download_uses_fallback_name_for_url_without_filename(
    tmp_path: Path,
) -> None:
    """Requirement: URLs without a filename get an image_N fallback name."""
    assets_dir = tmp_path / "assets"
    url = "https://example.com/images/"
    with patch("urllib.request.urlretrieve", side_effect=_write_bytes):
        url_map = download_assets_to_dir([url], assets_dir)
    if not next(iter(url_map.values())).startswith("assets/image_"):
        raise AssertionError(url_map)


# ---------------------------------------------------------------------------
# DownloadAssetError
# ---------------------------------------------------------------------------


def test_download_asset_error_str_contains_url_and_reason() -> None:
    """Requirement: DownloadAssetError message includes URL and reason."""
    error = DownloadAssetError("https://example.com/img.png", "timeout")
    msg = str(error)
    if "https://example.com/img.png" not in msg:
        raise AssertionError(msg)
    if "timeout" not in msg:
        raise AssertionError(msg)


def test_download_raises_on_unsupported_scheme(tmp_path: Path) -> None:
    """Requirement: DownloadAssetError raised for unsupported URL schemes."""
    assets_dir = tmp_path / "assets"
    url = "data:image/png;base64,abc"
    with pytest.raises(DownloadAssetError) as exc_info:
        download_assets_to_dir([url], assets_dir)
    if exc_info.value.url != url:
        raise AssertionError(exc_info.value)


def test_download_raises_on_private_host(tmp_path: Path) -> None:
    """Requirement: DownloadAssetError raised for private/loopback hosts."""
    dest = tmp_path / "out.png"
    private_urls = [
        "http://localhost/img.png",
        "http://127.0.0.1/img.png",
    ]
    for url in private_urls:
        with pytest.raises(DownloadAssetError) as exc_info:
            _fetch_url(url, dest)
        if exc_info.value.url != url:
            raise AssertionError(exc_info.value)


def test_fetch_url_raises_on_missing_host(tmp_path: Path) -> None:
    """Requirement: DownloadAssetError raised when URL has no host."""
    dest = tmp_path / "out.png"
    with pytest.raises(DownloadAssetError) as exc_info:
        _fetch_url("http:///no-host/img.png", dest)
    if exc_info.value.url != "http:///no-host/img.png":
        raise AssertionError(exc_info.value)


def test_is_private_host_ignores_unparseable_addr() -> None:
    """Requirement: _is_private_host skips entries ip_address cannot parse."""
    # Simulate an addr string that triggers ValueError in ip_address.
    # This branch is purely defensive; we force it via mock.
    good_entry = (None, None, None, None, ("93.184.216.34", 0))
    with (
        patch("socket.getaddrinfo", return_value=[good_entry]),
        patch.object(ipaddress, "ip_address", side_effect=ValueError("bad")),
    ):
        result = _is_private_host("example.com")
    if result:
        msg = "expected False when all addr strings are unparseable"
        raise AssertionError(msg)


# ---------------------------------------------------------------------------
# rewrite_image_paths — remote_map branch
# ---------------------------------------------------------------------------


def test_rewrite_replaces_remote_url_with_assets_relative() -> None:
    """Requirement: rewrite_image_paths substitutes remote URLs."""
    url = "https://example.com/chart.png"
    remote_map = {url: "assets/chart.png"}
    markdown = f"![fig]({url})"
    result = rewrite_image_paths(markdown, {}, remote_map)
    if "assets/chart.png" not in result:
        raise AssertionError(result)


# ---------------------------------------------------------------------------
# Integration: save with remote copy_assets
# ---------------------------------------------------------------------------


def test_save_copy_assets_downloads_remote_image(tmp_path: Path) -> None:
    """Requirement: copy_assets=True downloads remote images into assets/."""
    url = "https://example.com/chart.png"
    output = tmp_path / "report.md"
    report = Report("R").add(Chapter("C").add(Image(url, alt="chart")))
    with patch("urllib.request.urlretrieve", side_effect=_write_bytes):
        report.save(output, copy_assets=True)
    content = output.read_text(encoding="utf-8")
    if "assets/chart.png" not in content:
        raise AssertionError(content)
    if not (tmp_path / "assets" / "chart.png").exists():
        msg = "remote asset not written"
        raise AssertionError(msg)


def test_save_raises_download_error_when_remote_unreachable(
    tmp_path: Path,
) -> None:
    """Requirement: save() raises DownloadAssetError if download fails."""
    url = "https://example.com/missing.png"
    output = tmp_path / "report.md"
    report = Report("R").add(Chapter("C").add(Image(url, alt="missing")))
    with (
        patch("urllib.request.urlretrieve", side_effect=URLError("timeout")),
        pytest.raises(DownloadAssetError),
    ):
        report.save(output, copy_assets=True)
