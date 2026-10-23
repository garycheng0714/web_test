import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from web_test.command import CommandResult
from web_test.write_guard import ALLOWED_DIRS


@dataclass(frozen=True)
class AutomationEvidence:
    """What a red automation run needs for a human to diagnose it."""

    pytest_output: str | None = None
    pytest_runs: int = 0
    suite: CommandResult | None = None
    files: tuple[str, ...] = ()
    trace: tuple[str, ...] = ()


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
        "",
        "### Pytest output",
        "",
        _fenced(evidence.pytest_output or "no pytest output"),
        "",
        "### Suite output",
        "",
        _fenced(_suite_text(evidence.suite)),
        "",
        "### Tool trace",
        "",
        _fenced("\n".join(evidence.trace) if evidence.trace else "trace unavailable"),
    ]
    return "\n".join(lines)


def _copy_generated(
    workspace: Path, directory: Path, relative: str
) -> None:
    candidate = PurePosixPath(relative)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or ".." in candidate.parts
        or candidate.parts[0] not in ALLOWED_DIRS
        or candidate.suffix != ".py"
    ):
        return
    source = workspace / Path(*candidate.parts)
    if not source.is_file():
        return
    try:
        resolved = source.resolve()
    except OSError:
        return
    if not resolved.is_relative_to(workspace.resolve()):
        return
    target = directory / "files" / Path(*candidate.parts)
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

    return summary
