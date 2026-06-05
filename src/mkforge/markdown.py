"""Public GitHub Flavored Markdown rendering functions."""

from __future__ import annotations

from pathlib import Path

from mkforge.document import Report
from mkforge.input_checks import require_path
from mkforge.markdown_rendering import render_report_blocks


def render_report(report: Report) -> str:
    """Render a report to GitHub Flavored Markdown.

    Args:
        report: Report tree to render.

    Returns:
        Markdown document text.
    """
    _validate_report(report)
    return "\n\n".join(render_report_blocks(report))


def save_report(report: Report, path: str | Path) -> None:
    """Render a report and write it to a UTF-8 Markdown file.

    Args:
        report: Report tree to render.
        path: Destination path.
    """
    _validate_report(report)
    require_path(path, "save path")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_report(report), encoding="utf-8")


def _validate_report(report: object) -> None:
    """Validate a renderable report object.

    Args:
        report: Candidate report.
    """
    from mkforge.document import Report  # noqa: PLC0415

    if not isinstance(report, Report):
        message = f"report must be a Report; got {type(report).__name__}."
        raise TypeError(message)
