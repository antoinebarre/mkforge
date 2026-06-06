"""Asset management for report save operations.

Handles collection, verification, and copying of image assets referenced in
a report tree.  Local images are verified to exist on disk.  When
``copy_assets`` is requested, both local and remote images are copied into
an ``assets/`` directory next to the output file and Markdown links are
rewritten.

Remote images (URLs containing ``://``, protocol-relative ``//`` paths, or
``www.`` prefixes) are downloaded via ``urllib.request``.  A download failure
raises ``DownloadAssetError``.

This module is used exclusively by ``rendering.save_report``.

Import strategy
---------------
``Image``, ``Chapter``, ``Section``, and ``Report`` are imported inside
functions rather than at module level (annotated ``# noqa: PLC0415``).  This
breaks the circular import that would otherwise arise from:

    assets → content.image → (transitive) → rendering → assets

Deferred imports are the standard Python idiom for this pattern.  Do not
move them to the module level without verifying that the import cycle is
resolved by other means.
"""

from __future__ import annotations

import ipaddress
import shutil
import socket
import urllib.parse
import urllib.request
import warnings
from collections.abc import Sequence
from pathlib import Path
from urllib.error import URLError

from mkforge.errors import DownloadAssetError, MissingAssetError


def _is_remote(path: str) -> bool:
    """Return True if the path is a remote reference.

    A path is remote when it contains a URI scheme (``://``), uses a
    protocol-relative URL (``//``), or starts with ``www.``.  Everything
    else is treated as a local filesystem path.

    Args:
        path: Image path string to classify.

    Returns:
        True when the path is a remote reference.
    """
    return "://" in path or path.startswith(("//", "www."))


def collect_local_image_paths(report: object) -> list[Path]:
    """Walk a report tree and return resolved paths for all local images.

    Remote URLs are excluded.  Paths are resolved relative to the current
    working directory at call time.

    Args:
        report: Report instance to inspect.

    Returns:
        List of resolved ``Path`` objects for every local ``Image`` in the
        report tree, in document order.  Duplicates are preserved so that
        all occurrences can be reported.
    """
    from mkforge.content.image import Image  # noqa: PLC0415
    from mkforge.document import Chapter, Report, Section  # noqa: PLC0415

    if not isinstance(report, Report):
        return []

    results: list[Path] = []

    def _walk_children(children: Sequence[object]) -> None:
        """Recursively collect local image paths from a child sequence.

        Args:
            children: Sequence of Chapter, Section, or content element nodes.
        """
        for child in children:
            if isinstance(child, Image) and not _is_remote(child.path):
                results.append(Path(child.path).resolve())
            elif isinstance(child, (Chapter, Section)):
                _walk_children(child.children)

    _walk_children(report.children)
    return results


def collect_remote_image_urls(report: object) -> list[str]:
    """Walk a report tree and return URLs for all remote images.

    Local paths are excluded.

    Args:
        report: Report instance to inspect.

    Returns:
        List of remote URL strings for every remote ``Image`` in the report
        tree, in document order.  Duplicates are preserved.
    """
    from mkforge.content.image import Image  # noqa: PLC0415
    from mkforge.document import Chapter, Report, Section  # noqa: PLC0415

    if not isinstance(report, Report):
        return []

    results: list[str] = []

    def _walk_children(children: Sequence[object]) -> None:
        """Recursively collect remote image URLs from a child sequence.

        Args:
            children: Sequence of Chapter, Section, or content element nodes.
        """
        for child in children:
            if isinstance(child, Image) and _is_remote(child.path):
                results.append(child.path)
            elif isinstance(child, (Chapter, Section)):
                _walk_children(child.children)

    _walk_children(report.children)
    return results


def verify_assets(paths: list[Path]) -> None:
    """Verify that all given local paths exist on disk.

    Args:
        paths: Resolved local image paths to check.

    Raises:
        MissingAssetError: If any path does not exist, listing all missing
            paths in one error.
    """
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise MissingAssetError(missing)


def _unique_dest_name(
    base_name: str,
    used_names: dict[str, int],
    stem: str,
    suffix: str,
) -> str:
    """Compute a unique destination filename, renaming on collision.

    Args:
        base_name: Original filename (stem + suffix).
        used_names: Mutable map from base_name to next collision counter.
        stem: Filename stem without extension.
        suffix: Filename extension including the dot.

    Returns:
        Unique destination filename, possibly suffixed with a counter.
    """
    if base_name in used_names:
        counter = used_names[base_name]
        used_names[base_name] = counter + 1
        dest_name = f"{stem}_{counter}{suffix}"
        msg = f"Asset name collision: {base_name!r} renamed to {dest_name!r}."
        warnings.warn(msg, UserWarning, stacklevel=4)
        return dest_name
    used_names[base_name] = 1
    return base_name


def copy_assets_to_dir(
    paths: list[Path],
    assets_dir: Path,
) -> dict[Path, str]:
    """Copy local image files into the assets directory.

    Files that share a filename with an already-copied file are renamed by
    appending a one-based counter suffix before the extension
    (e.g. ``chart.png`` → ``chart_1.png``).  A ``UserWarning`` is emitted
    for each renamed file.

    Args:
        paths: Resolved local image paths to copy (duplicates skipped).
        assets_dir: Destination directory; created if it does not exist.

    Returns:
        Mapping from each original resolved path to its new relative
        ``assets/<filename>`` string for use in Markdown link rewriting.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    path_map: dict[Path, str] = {}
    used_names: dict[str, int] = {}

    for src in paths:
        if src in path_map:
            continue
        dest_name = _unique_dest_name(
            src.name,
            used_names,
            src.stem,
            src.suffix,
        )
        shutil.copy2(src, assets_dir / dest_name)
        path_map[src] = f"assets/{dest_name}"

    return path_map


_ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https", "ftp", "ftps"})


def _ip_is_non_routable(
    addr: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> bool:
    """Return True when the IP address is non-routable.

    Covers loopback, link-local, private, unspecified, and multicast ranges.

    Args:
        addr: Resolved IP address to classify.

    Returns:
        True when the address must not be contacted.
    """
    return (
        addr.is_loopback
        or addr.is_link_local
        or addr.is_private
        or addr.is_unspecified
        or addr.is_multicast
    )


def _is_private_host(hostname: str) -> bool:
    """Return True when the hostname resolves to a non-routable IP address.

    Blocks loopback, link-local, private (RFC 1918 / RFC 4193), and
    unspecified addresses to prevent SSRF attacks against internal services
    such as cloud metadata endpoints (e.g. 169.254.169.254) or the host
    network.

    Args:
        hostname: DNS name or IP address string to check.

    Returns:
        True when any resolved IP is non-routable.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            addr = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if _ip_is_non_routable(addr):
            return True
    return False


def _fetch_url(url: str, dest_path: Path) -> None:
    """Validate and download a single URL to a local path.

    Two security checks run before any network call:

    1. Scheme validation — only ``http``, ``https``, ``ftp``, and ``ftps``
       are accepted; all others raise ``DownloadAssetError`` immediately.
    2. Host validation — the hostname is resolved via ``socket.getaddrinfo``
       and every resulting IP address is checked against non-routable ranges
       (loopback, link-local, RFC 1918 private, unspecified, multicast).
       Any private resolution raises ``DownloadAssetError`` to prevent SSRF
       attacks against internal services such as cloud metadata endpoints.

    The ``urlretrieve`` call is suppressed by ``# noqa: S310  # nosec B310``
    because both Ruff (S310) and Bandit (B310) flag it as an unaudited URL
    open.  The suppression is justified: the scheme and host are validated
    immediately above in this function, so the call is safe by construction.
    Do not move or reorder the validation and ``urlretrieve`` lines without
    re-evaluating the security contract.

    Args:
        url: Remote URL to download.
        dest_path: Local path where the downloaded file will be written.

    Raises:
        DownloadAssetError: If the scheme is not allowed, the host resolves
            to a private address, or the download fails.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        msg = f"Unsupported URL scheme {parsed.scheme!r}."
        raise DownloadAssetError(url, msg)
    hostname = parsed.hostname or ""
    if not hostname:
        raise DownloadAssetError(url, "URL has no host.")
    if _is_private_host(hostname):
        msg = f"Host {hostname!r} resolves to a private or loopback address."
        raise DownloadAssetError(url, msg)
    try:
        urllib.request.urlretrieve(url, dest_path)  # noqa: S310  # nosec B310
    except URLError as exc:
        raise DownloadAssetError(url, str(exc)) from exc


def download_assets_to_dir(
    urls: list[str],
    assets_dir: Path,
) -> dict[str, str]:
    """Download remote image URLs into the assets directory.

    Files that share a derived filename with an already-downloaded file are
    renamed by appending a one-based counter suffix.  A ``UserWarning`` is
    emitted for each renamed file.

    The filename is derived from the last path segment of the URL.  If the
    URL has no usable filename, ``image_<n>`` is used.

    Each URL is validated before any network call: the scheme must belong to
    the allowed set and the hostname must not resolve to a private or loopback
    address (SSRF protection).

    Args:
        urls: Remote image URL strings to download (duplicates skipped).
        assets_dir: Destination directory; created if it does not exist.

    Returns:
        Mapping from each original URL to its new relative
        ``assets/<filename>`` string for use in Markdown link rewriting.

    Raises:
        DownloadAssetError: If any URL cannot be fetched or fails validation.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    url_map: dict[str, str] = {}
    used_names: dict[str, int] = {}
    fallback_counter = 0

    for url in urls:
        if url in url_map:
            continue
        raw_name = Path(url.split("?")[0].rstrip("/")).name
        if not raw_name or "." not in raw_name:
            fallback_counter += 1
            raw_name = f"image_{fallback_counter}"
        stem = Path(raw_name).stem
        suffix = Path(raw_name).suffix
        dest_name = _unique_dest_name(raw_name, used_names, stem, suffix)
        dest_path = assets_dir / dest_name
        _fetch_url(url, dest_path)
        url_map[url] = f"assets/{dest_name}"

    return url_map


def rewrite_image_paths(
    markdown: str,
    local_map: dict[Path, str],
    remote_map: dict[str, str] | None = None,
) -> str:
    """Rewrite image paths in rendered Markdown using the copy/download maps.

    Replaces each original path or URL string that appears in a Markdown
    image reference with its new ``assets/<filename>`` relative path.

    Args:
        markdown: Rendered Markdown document string.
        local_map: Mapping from resolved local path to new relative path,
            as returned by ``copy_assets_to_dir``.
        remote_map: Mapping from remote URL to new relative path, as
            returned by ``download_assets_to_dir``.  ``None`` is treated
            as an empty map.

    Returns:
        Markdown string with image paths rewritten to ``assets/`` locations.
    """
    for src_path, dest_rel in local_map.items():
        markdown = markdown.replace(str(src_path), dest_rel)
        markdown = markdown.replace(src_path.name, dest_rel)
    for url, dest_rel in (remote_map or {}).items():
        markdown = markdown.replace(url, dest_rel)
    return markdown
