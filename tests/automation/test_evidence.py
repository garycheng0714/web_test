from pathlib import Path

from web_test.automation import evidence as evidence_module
from web_test.automation.evidence import (
    MAX_TRACE_FILES,
    AutomationEvidence,
    collect_traces,
    render_summary,
    write_evidence,
)
from web_test.automation.quality import QualityFinding, QualityRule
from web_test.command import CommandResult


def test_write_evidence_keeps_outputs_and_allowed_files(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    (workspace / "tests").mkdir(parents=True)
    (workspace / "tests" / "test_a.py").write_text("def test_a(): pass\n", encoding="utf-8")
    (workspace / ".venv").mkdir()
    (workspace / ".venv" / "secret.py").write_text("secret\n", encoding="utf-8")
    evidence = AutomationEvidence(
        pytest_output="agent red output",
        pytest_runs=2,
        suite=CommandResult(1, "suite stdout", "suite stderr"),
        files=("tests/test_a.py", ".venv/secret.py", "../escape.py"),
        trace=("-> uv run pytest",),
    )
    directory = tmp_path / "evidence"

    summary = write_evidence(
        status="agent_red",
        error=None,
        evidence=evidence,
        workspace=workspace,
        directory=directory,
    )

    assert "Automation run: `agent_red`" in summary
    assert "agent red output" in summary
    assert "suite stderr" in summary
    assert (directory / "summary.md").read_text(encoding="utf-8") == summary + "\n"
    assert (directory / "pytest-output.txt").read_text(encoding="utf-8") == (
        "agent red output\n"
    )
    assert (directory / "suite-output.txt").read_text(encoding="utf-8").startswith(
        "exit: 1"
    )
    assert (directory / "trace.txt").read_text(encoding="utf-8") == "-> uv run pytest\n"
    assert (directory / "files" / "tests" / "test_a.py").is_file()
    assert not (directory / "files" / ".venv" / "secret.py").exists()
    assert not (directory / "files" / "escape.py").exists()


def test_render_summary_includes_quality_findings() -> None:
    evidence = AutomationEvidence(
        quality=(
            QualityFinding(QualityRule.CASE_MARKER, "tests/test_a.py:1: no marker"),
        )
    )

    summary = render_summary("quality_red", None, evidence)

    assert "### Quality gate" in summary
    assert "**case_marker**: tests/test_a.py:1: no marker" in summary


def test_render_summary_without_evidence() -> None:
    summary = render_summary("failed", "boom", None)

    assert "Automation run: `failed`" in summary
    assert "Error: boom" in summary
    assert "No evidence was captured." in summary


def test_write_evidence_does_not_copy_a_symlink_outside_the_workspace(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "repo"
    (workspace / "tests").mkdir(parents=True)
    secret = tmp_path / "secret.py"
    secret.write_text("secret\n", encoding="utf-8")
    (workspace / "tests" / "link.py").symlink_to(secret)
    evidence = AutomationEvidence(files=("tests/link.py",))
    directory = tmp_path / "evidence"

    write_evidence(
        status="failed",
        error=None,
        evidence=evidence,
        workspace=workspace,
        directory=directory,
    )

    assert not (directory / "files" / "tests" / "link.py").exists()


def test_write_evidence_copies_traces(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    trace = workspace / "test-results" / "suite" / "a" / "trace.zip"
    trace.parent.mkdir(parents=True)
    trace.write_bytes(b"trace")
    evidence = AutomationEvidence(traces=("test-results/suite/a/trace.zip",))
    directory = tmp_path / "evidence"

    summary = write_evidence(
        status="suite_red",
        error=None,
        evidence=evidence,
        workspace=workspace,
        directory=directory,
    )

    assert (
        directory / "traces" / "test-results" / "suite" / "a" / "trace.zip"
    ).read_bytes() == b"trace"
    assert "test-results/suite/a/trace.zip" in summary


def test_write_evidence_skips_disallowed_traces(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    relative_paths = (
        ".venv/secret.zip",
        ".playwright-cli/state.zip",
        "test-results/../escape.zip",
        "test-results/not-a-trace.txt",
    )
    for relative in relative_paths:
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
    evidence = AutomationEvidence(traces=relative_paths)
    directory = tmp_path / "evidence"

    write_evidence(
        status="suite_red",
        error=None,
        evidence=evidence,
        workspace=workspace,
        directory=directory,
    )

    assert not (directory / "traces").exists()


def test_collect_traces_caps_the_file_count(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    root = workspace / "test-results"
    root.mkdir(parents=True)
    for index in range(MAX_TRACE_FILES + 1):
        (root / f"{index}.zip").write_bytes(b"x")

    traces, skipped = collect_traces(workspace)

    assert len(traces) == MAX_TRACE_FILES
    assert skipped == 1


def test_collect_traces_caps_the_total_size(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(evidence_module, "MAX_TRACE_BYTES", 10)
    workspace = tmp_path / "repo"
    root = workspace / "test-results"
    root.mkdir(parents=True)
    (root / "a.zip").write_bytes(b"x" * 8)
    (root / "b.zip").write_bytes(b"x" * 8)

    traces, skipped = collect_traces(workspace)

    assert traces == ("test-results/a.zip",)
    assert skipped == 1


def test_render_summary_says_when_no_trace_was_produced() -> None:
    summary = render_summary("published", None, AutomationEvidence())

    assert "no trace produced" in summary


def test_render_summary_notes_skipped_traces() -> None:
    summary = render_summary(
        "suite_red",
        None,
        AutomationEvidence(
            traces=("test-results/a.zip",),
            traces_skipped=2,
        ),
    )

    assert "2 trace(s) skipped" in summary
