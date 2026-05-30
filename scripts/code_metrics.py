"""Check code metrics configured in pyproject.toml."""

from __future__ import annotations

import ast
import fnmatch
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

type TomlValue = str | int | float | bool | list[object]


@dataclass(frozen=True)
class MetricsConfig:
    """Code metrics thresholds.

    Attributes:
        paths: Python paths to inspect.
        exclude: Glob patterns to exclude.
        max_cyclomatic_complexity: Maximum complexity for one block.
        max_average_complexity: Maximum average block complexity.
        min_maintainability_index: Minimum maintainability index per file.
        max_module_logical_lines: Maximum logical lines per module.
        max_module_source_lines: Maximum source lines per module.
    """

    paths: tuple[Path, ...]
    exclude: tuple[str, ...]
    max_cyclomatic_complexity: int
    max_average_complexity: float
    min_maintainability_index: float
    max_module_logical_lines: int
    max_module_source_lines: int


@dataclass(frozen=True)
class BlockMetric:
    """Complexity metric for one block.

    Attributes:
        label: Block label.
        complexity: Cyclomatic complexity value.
    """

    label: str
    complexity: int


@dataclass(frozen=True)
class FileMetric:
    """Metrics for one Python file.

    Attributes:
        path: File path.
        logical_lines: Non-empty, non-comment lines.
        source_lines: Physical source lines.
        maintainability_index: Maintainability score.
        blocks: Function and method metrics.
    """

    path: Path
    logical_lines: int
    source_lines: int
    maintainability_index: float
    blocks: tuple[BlockMetric, ...]


@dataclass(frozen=True)
class MetricResult:
    """One metric comparison.

    Attributes:
        name: Metric name.
        expected: Expected value.
        actual: Actual value.
        passed: Whether the metric passed.
    """

    name: str
    expected: str
    actual: str
    passed: bool


@dataclass(frozen=True)
class MetricsSummary:
    """Compact code metrics summary.

    Attributes:
        max_complexity: Highest cyclomatic complexity.
        average_complexity: Average block cyclomatic complexity.
        min_maintainability_index: Lowest file maintainability index.
    """

    max_complexity: int
    average_complexity: float
    min_maintainability_index: float


def main() -> int:
    """Run code metric checks.

    Returns:
        Process exit code.
    """
    config = _load_config(Path("pyproject.toml"))
    metrics = tuple(_file_metric(path) for path in _iter_python_files(config))
    summary = _metrics_summary(metrics)
    results = _metric_results(config, metrics, summary)
    failed = any(not result.passed for result in results)
    _write_line(_status_line(failed=failed, summary=summary))
    _write_results(results)
    return int(failed)


def _load_config(path: Path) -> MetricsConfig:
    """Load code metric thresholds from TOML.

    Args:
        path: Project TOML path.

    Returns:
        Parsed metrics configuration.
    """
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    table = raw["tool"]["mkforge"]["code_metrics"]
    return MetricsConfig(
        paths=tuple(Path(value) for value in _string_tuple(table["paths"])),
        exclude=_string_tuple(table.get("exclude", [])),
        max_cyclomatic_complexity=int(table["max_cyclomatic_complexity"]),
        max_average_complexity=float(table["max_average_complexity"]),
        min_maintainability_index=float(table["min_maintainability_index"]),
        max_module_logical_lines=int(table["max_module_logical_lines"]),
        max_module_source_lines=int(table["max_module_source_lines"]),
    )


def _string_tuple(value: TomlValue) -> tuple[str, ...]:
    """Convert a TOML array to a string tuple.

    Args:
        value: TOML value.

    Returns:
        Tuple of strings.

    Raises:
        TypeError: If value is not a list.
    """
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    message = "Expected a TOML array"
    raise TypeError(message)


def _iter_python_files(config: MetricsConfig) -> tuple[Path, ...]:
    """Find Python files covered by metrics.

    Args:
        config: Metrics configuration.

    Returns:
        Python files to inspect.
    """
    files: list[Path] = []
    for path in config.paths:
        files.extend(_path_python_files(path))
    return tuple(
        file_path
        for file_path in sorted(files)
        if not _is_excluded(file_path, config.exclude)
    )


def _path_python_files(path: Path) -> tuple[Path, ...]:
    """Return Python files below a path.

    Args:
        path: File or directory path.

    Returns:
        Python files under the path.
    """
    if path.is_file() and path.suffix == ".py":
        return (path,)
    return tuple(path.rglob("*.py"))


def _is_excluded(path: Path, patterns: tuple[str, ...]) -> bool:
    """Return whether a file matches an exclusion pattern.

    Args:
        path: Candidate path.
        patterns: Glob patterns.

    Returns:
        True if the path is excluded.
    """
    normalized = path.as_posix()
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def _file_metric(path: Path) -> FileMetric:
    """Measure one Python file.

    Args:
        path: Python file path.

    Returns:
        File metrics.
    """
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)
    logical_lines = _logical_line_count(lines)
    blocks = _block_metrics(path, tree)
    maintainability = _maintainability_index(logical_lines, blocks)
    return FileMetric(path, logical_lines, len(lines), maintainability, blocks)


def _logical_line_count(lines: list[str]) -> int:
    """Count logical source lines.

    Args:
        lines: Source lines.

    Returns:
        Count of non-empty, non-comment lines.
    """
    return sum(1 for line in lines if _is_logical_line(line))


def _is_logical_line(line: str) -> bool:
    """Return whether a line counts as logical code.

    Args:
        line: Source line.

    Returns:
        True for non-empty, non-comment lines.
    """
    stripped = line.strip()
    return bool(stripped and not stripped.startswith("#"))


def _block_metrics(path: Path, tree: ast.AST) -> tuple[BlockMetric, ...]:
    """Collect complexity for functions and methods.

    Args:
        path: File path.
        tree: Parsed AST.

    Returns:
        Block metrics.
    """
    return tuple(
        BlockMetric(f"{path}:{node.lineno} {node.name}", _complexity(node))
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    )


def _complexity(node: ast.AST) -> int:
    """Compute simple cyclomatic complexity for an AST node.

    Args:
        node: AST node to inspect.

    Returns:
        Cyclomatic complexity.
    """
    return 1 + sum(_decision_weight(child) for child in ast.walk(node))


def _decision_weight(node: ast.AST) -> int:
    """Return the complexity contribution of one AST node.

    Args:
        node: AST node.

    Returns:
        Complexity increment.
    """
    if isinstance(node, ast.BoolOp):
        return max(0, len(node.values) - 1)
    if isinstance(node, ast.Try):
        return len(node.handlers)
    if isinstance(node, ast.Match):
        return len(node.cases)
    decision_nodes = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.IfExp,
        ast.ExceptHandler,
        ast.comprehension,
    )
    return int(isinstance(node, decision_nodes))


def _maintainability_index(
    logical_lines: int,
    blocks: tuple[BlockMetric, ...],
) -> float:
    """Compute a lightweight maintainability score.

    Args:
        logical_lines: Logical line count.
        blocks: Block metrics.

    Returns:
        Maintainability score from 0 to 100.
    """
    max_complexity = max((block.complexity for block in blocks), default=1)
    score = 100.0 - (max_complexity - 1) * 4.0 - logical_lines * 0.05
    return max(0.0, round(score, 2))


def _metric_results(
    config: MetricsConfig,
    metrics: tuple[FileMetric, ...],
    summary: MetricsSummary,
) -> tuple[MetricResult, ...]:
    """Build metric threshold comparisons.

    Args:
        config: Metrics thresholds.
        metrics: File metrics.
        summary: Compact aggregate metrics.

    Returns:
        Metric comparisons.
    """
    blocks = tuple(block for metric in metrics for block in metric.blocks)
    max_block = max(blocks, key=lambda item: item.complexity, default=None)
    min_mi = min(metrics, key=lambda item: item.maintainability_index)
    max_lloc = max(metrics, key=lambda item: item.logical_lines)
    max_sloc = max(metrics, key=lambda item: item.source_lines)
    max_complexity = max_block.complexity if max_block else 0
    max_label = max_block.label if max_block else "no analyzed block"
    return (
        MetricResult(
            "Max cyclomatic complexity",
            f"<= {config.max_cyclomatic_complexity}",
            f"{max_complexity} ({max_label})",
            summary.max_complexity <= config.max_cyclomatic_complexity,
        ),
        MetricResult(
            "Average cyclomatic complexity",
            f"<= {config.max_average_complexity:.2f}",
            f"{summary.average_complexity:.2f}",
            summary.average_complexity <= config.max_average_complexity,
        ),
        MetricResult(
            "Minimum maintainability index",
            f">= {config.min_maintainability_index:.2f}",
            f"{min_mi.maintainability_index:.2f} ({min_mi.path})",
            summary.min_maintainability_index
            >= config.min_maintainability_index,
        ),
        MetricResult(
            "Max module logical lines",
            f"<= {config.max_module_logical_lines}",
            f"{max_lloc.logical_lines} ({max_lloc.path})",
            max_lloc.logical_lines <= config.max_module_logical_lines,
        ),
        MetricResult(
            "Max module source lines",
            f"<= {config.max_module_source_lines}",
            f"{max_sloc.source_lines} ({max_sloc.path})",
            max_sloc.source_lines <= config.max_module_source_lines,
        ),
    )


def _metrics_summary(metrics: tuple[FileMetric, ...]) -> MetricsSummary:
    """Create compact aggregate code metrics.

    Args:
        metrics: File metrics.

    Returns:
        Compact metrics summary.
    """
    blocks = tuple(block for metric in metrics for block in metric.blocks)
    max_complexity = max((block.complexity for block in blocks), default=0)
    min_maintainability = min(
        metric.maintainability_index for metric in metrics
    )
    return MetricsSummary(
        max_complexity,
        _average_complexity(blocks),
        min_maintainability,
    )


def _average_complexity(blocks: tuple[BlockMetric, ...]) -> float:
    """Return average block complexity.

    Args:
        blocks: Block metrics.

    Returns:
        Average complexity.
    """
    if not blocks:
        return 0.0
    return sum(block.complexity for block in blocks) / len(blocks)


def _status_line(*, failed: bool, summary: MetricsSummary) -> str:
    """Return the compact console status line.

    Args:
        failed: Whether at least one metric failed.
        summary: Code metrics summary.

    Returns:
        Status line for the check runner.
    """
    status = "failed" if failed else "passed"
    return (
        f"Code metrics {status}: "
        f"max CC {summary.max_complexity}, "
        f"avg CC {summary.average_complexity:.2f}, "
        f"min MI {summary.min_maintainability_index:.2f}"
    )


def _write_results(results: tuple[MetricResult, ...]) -> None:
    """Write metric results as a table.

    Args:
        results: Metric results to print.
    """
    name_width = max(len("Metric"), *(len(item.name) for item in results))
    expected_width = max(
        len("Expected"),
        *(len(item.expected) for item in results),
    )
    _write_line("")
    _write_line(
        f"{'Metric':<{name_width}}  {'Expected':<{expected_width}}  Actual",
    )
    _write_line(f"{'-' * name_width}  {'-' * expected_width}  {'-' * 48}")
    for item in results:
        status = "PASSED" if item.passed else "FAILED"
        _write_line(
            f"{item.name:<{name_width}}  "
            f"{item.expected:<{expected_width}}  "
            f"{item.actual:<48}  "
            f"{status}",
        )
    _write_line("")


def _write_line(message: str) -> None:
    """Write one line to standard output.

    Args:
        message: Text to write.
    """
    sys.stdout.write(f"{message}\n")


if __name__ == "__main__":
    raise SystemExit(main())
