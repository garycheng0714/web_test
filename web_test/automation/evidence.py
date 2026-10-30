import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from web_test.automation.quality import QualityFinding
from web_test.automation.report import RunReport, render_run_report
from web_test.command import CommandResult
from web_test.write_guard import ALLOWED_DIRS, resolve_workspace_path

# Keep the artifact bounded: a trace can be several MB, and the evidence is best-effort.
MAX_TRACE_FILES = 20
MAX_TRACE_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class AutomationEvidence:
    """What a red automation run needs for a human to diagnose it."""

    pytest_output: str | None = None
    pytest_runs: int = 0
    suite: CommandResult | None = None
    files: tuple[str, ...] = ()
    quality: tuple[QualityFinding, ...] = ()
    report: RunReport | None = None
    trace: tuple[str, ...] = ()
    traces: tuple[str, ...] = ()
    traces_skipped: int = 0


def _fenced(text: str) -> str:
    return f"~~~text\n{text.rstrip()}\n~~~"


def _suite_text(suite: CommandResult | None) -> str:
    if suite is None:
        return "the suite was not run"
    return (
        f"exit: {suite.returncode}\n\n"
        f"--- stdout ---\n{suite.stdout.rstrip()}\n\n"
        f"--- stderr ---\n{suite.stderr.rstrip()}"
    )


def collect_traces(workspace: Path) -> tuple[tuple[str, ...], int]:
    """The failing tests' traces, capped for the artifact. Best-effort."""
    root = workspace / "test-results"
    try:
        candidates = sorted(path for path in root.rglob("*.zip") if path.is_file())
    except OSError:
        return (), 0

    traces: list[str] = []
    skipped = 0
    total = 0
    workspace_root = workspace.resolve()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if not resolved.is_relative_to(workspace_root):
            continue
        if len(traces) >= MAX_TRACE_FILES:
            skipped += 1
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if total + size > MAX_TRACE_BYTES:
            skipped += 1
            continue
        total += size
        traces.append(path.relative_to(workspace).as_posix())
    return tuple(traces), skipped


def render_summary(
    status: str,
    error: str | None,
    evidence: AutomationEvidence | None,
) -> str:
    """Render the summary that goes to the job summary and `summary.md`."""
    lines = [
        f"## Automation run: `{status}`",
        "",
        f"- Error: {error or 'none'}",
    ]
    if evidence is None:
        lines += ["", "No evidence was captured."]
        return "\n".join(lines)

    lines += [
        f"- Pytest runs: {evidence.pytest_runs}",
        f"- Generated files: {', '.join(evidence.files) if evidence.files else 'none'}",
    ]
    if evidence.quality:
        lines += ["", "### Quality gate", ""]
        lines += [f"- **{finding.rule}**: {finding.detail}" for finding in evidence.quality]
    if evidence.report is not None:
        lines += ["", render_run_report(evidence.report)]
    lines += [
        "",
        "### Pytest output",
        "",
        _fenced(evidence.pytest_output or "no pytest output"),
        "",
        "### Suite output",
        "",
        _fenced(_suite_text(evidence.suite)),
        "",
        "### Traces",
        "",
        _fenced(
            "\n".join(evidence.traces)
            if evidence.traces
            else "no trace produced (green run or tracing unavailable)"
        ),
        *(["", "The files are copied under `traces/` in the artifact."] if evidence.traces else []),
        "",
        "### Tool trace",
        "",
        _fenced("\n".join(evidence.trace) if evidence.trace else "trace unavailable"),
    ]
    if evidence.traces_skipped:
        lines += [
            "",
            (
                f"{evidence.traces_skipped} trace(s) skipped by the "
                f"{MAX_TRACE_FILES}-file / {MAX_TRACE_BYTES // (1024 * 1024)}MB cap."
            ),
        ]
    return "\n".join(lines)


def _copy_generated(workspace: Path, directory: Path, relative: str) -> None:
    candidate = PurePosixPath(relative)
    if not candidate.parts or candidate.parts[0] not in ALLOWED_DIRS:
        return
    source = resolve_workspace_path(workspace, relative, suffix=".py")
    if source is None:
        return
    target = directory / "files" / Path(*candidate.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_trace(workspace: Path, directory: Path, relative: str) -> None:
    candidate = PurePosixPath(relative)
    if not candidate.parts or candidate.parts[0] != "test-results":
        return
    source = resolve_workspace_path(workspace, relative, suffix=".zip")
    if source is None:
        return
    target = directory / "traces" / Path(*candidate.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_evidence(
    *,
    status: str,
    error: str | None,
    evidence: AutomationEvidence | None,
    workspace: Path,
    directory: Path,
) -> str:
    """Write the evidence directory and return the summary markdown."""
    directory.mkdir(parents=True, exist_ok=True)
    summary = render_summary(status, error, evidence)
    (directory / "summary.md").write_text(summary + "\n", encoding="utf-8")

    if evidence is not None:
        (directory / "pytest-output.txt").write_text(
            (evidence.pytest_output or "no pytest output") + "\n",
            encoding="utf-8",
        )
        (directory / "suite-output.txt").write_text(
            _suite_text(evidence.suite) + "\n",
            encoding="utf-8",
        )
        (directory / "trace.txt").write_text(
            ("\n".join(evidence.trace) or "trace unavailable") + "\n",
            encoding="utf-8",
        )
        for relative in evidence.files:
            _copy_generated(workspace, directory, relative)
        for relative in evidence.traces:
            _copy_trace(workspace, directory, relative)

    return summary
