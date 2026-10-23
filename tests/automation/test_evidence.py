from pathlib import Path

from web_test.automation.evidence import (
    AutomationEvidence,
    render_summary,
    write_evidence,
)
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
