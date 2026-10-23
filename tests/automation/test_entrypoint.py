from pathlib import Path
from unittest.mock import ANY, MagicMock, call

from web_test.automation.coding_agent import AutomationResult
from web_test.automation.entrypoint import AutomationOutcome, AutomationStatus, automate
from web_test.command import CommandResult

SAMPLE = """\
---
id: test-case-0001
base_url: https://automationexercise.com
requirement_ids: [FR-CNT-01]
priority: High
test_type: Functional
---

# Test Case 6: Contact Us Form
"""


def _write_case(tmp_path: Path) -> Path:
    case_dir = tmp_path / "test-case"
    case_dir.mkdir()
    case = case_dir / "test-case-0001.md"
    case.write_text(SAMPLE, encoding="utf-8")
    return case


def _deps(*, files: list[str], green: bool) -> tuple[MagicMock, MagicMock, MagicMock]:
    git = MagicMock()
    git.changed_paths.return_value = list(files)
    pr = MagicMock()
    suite = MagicMock()
    suite.run.return_value = CommandResult(
        0 if green else 1, "suite stdout", "suite stderr"
    )
    return git, pr, suite


def test_automate_publishes_on_green(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="## Summary\n\nbody"))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.PUBLISHED)
    assert agent.call_args == call(SAMPLE, workspace_dir=tmp_path, deps=ANY)
    assert git.changed_paths.called
    assert pr.open_pull_request.called


def test_automate_skips_publish_when_the_agent_reports_red(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body=None))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.AGENT_RED)
    suite.run.assert_not_called()
    pr.assert_not_called()


def test_automate_skips_publish_when_the_suite_is_red(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=False)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.SUITE_RED)
    assert outcome.evidence is not None
    assert outcome.evidence.files == ("tests/a.py",)
    pr.assert_not_called()


def test_automate_skips_publish_when_nothing_changed(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=[], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.NO_CHANGES)
    pr.assert_not_called()


def test_automate_reports_a_non_artifact_path(tmp_path: Path) -> None:
    path = tmp_path / "test-case-0001.md"
    path.write_text(SAMPLE, encoding="utf-8")
    agent = MagicMock()
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(path, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.FAILED
    agent.assert_not_called()


def test_automate_reports_a_missing_case_file(tmp_path: Path) -> None:
    agent = MagicMock()
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(
        tmp_path / "test-case" / "test-case-missing.md",
        workspace=tmp_path,
        agent=agent,
        git=git,
        pr=pr,
        suite=suite,
    )

    assert outcome.status is AutomationStatus.FAILED
    agent.assert_not_called()


def test_automate_reports_invalid_front_matter(tmp_path: Path) -> None:
    directory = tmp_path / "test-case"
    directory.mkdir()
    path = directory / "test-case-broken.md"
    path.write_text("---\nid: test-case-broken\n---\n", encoding="utf-8")
    agent = MagicMock()
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(path, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.FAILED
    agent.assert_not_called()


def test_automate_reports_a_publish_failure(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)
    pr.open_pull_request.side_effect = RuntimeError("gh boom")

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.FAILED, error="gh boom")


def test_automate_reports_a_suite_failure(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)
    suite.run.side_effect = FileNotFoundError("uv")

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.FAILED


def test_automate_keeps_the_deciding_suite_output(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=False)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.evidence is not None
    assert outcome.evidence.suite == CommandResult(1, "suite stdout", "suite stderr")


def test_automate_captures_the_agent_pytest_output(tmp_path: Path) -> None:
    case = _write_case(tmp_path)

    def agent(text, *, workspace_dir, deps):
        deps.last_pytest_output = "agent red output"
        deps.pytest_runs = 2
        deps.tool_trace.append("-> uv run pytest")
        return AutomationResult(pr_body=None)

    git, pr, suite = _deps(files=[], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.AGENT_RED
    assert outcome.evidence is not None
    assert outcome.evidence.pytest_output == "agent red output"
    assert outcome.evidence.pytest_runs == 2
    assert "-> uv run pytest" in outcome.evidence.trace


def test_automate_captures_the_generated_files(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py", "pages/home.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.PUBLISHED
    assert outcome.evidence is not None
    assert outcome.evidence.files == ("tests/a.py", "pages/home.py")


def test_automate_keeps_red_evidence_when_git_fails(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=False)
    git.changed_paths.side_effect = RuntimeError("git boom")

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.SUITE_RED
    assert outcome.evidence is not None
    assert outcome.evidence.files == ()
