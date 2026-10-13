from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from web_test.automation.coding_agent import AutomationResult
from web_test.automation.entrypoint import AutomationOutcome, AutomationStatus, automate

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
    suite.is_green.return_value = green
    return git, pr, suite


def test_automate_publishes_on_green(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="## Summary\n\nbody"))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.PUBLISHED)
    assert agent.call_args == call(SAMPLE, workspace_dir=tmp_path)
    assert git.changed_paths.called
    assert pr.open_pull_request.called


def test_automate_skips_publish_when_the_agent_reports_red(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body=None))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.AGENT_RED)
    suite.is_green.assert_not_called()
    pr.assert_not_called()


def test_automate_skips_publish_when_the_suite_is_red(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=["tests/a.py"], green=False)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.SUITE_RED)
    git.changed_paths.assert_not_called()
    pr.assert_not_called()


def test_automate_skips_publish_when_nothing_changed(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="body"))
    git, pr, suite = _deps(files=[], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.NO_CHANGES)
    pr.assert_not_called()


def test_automate_rejects_a_non_artifact_path(tmp_path: Path) -> None:
    path = tmp_path / "test-case-0001.md"
    path.write_text(SAMPLE, encoding="utf-8")
    agent = MagicMock()
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    with pytest.raises(ValueError):
        automate(path, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)
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
    suite.is_green.side_effect = FileNotFoundError("uv")

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome.status is AutomationStatus.FAILED
