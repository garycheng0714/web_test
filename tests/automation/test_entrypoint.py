from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from pydantic import HttpUrl, ValidationError

from web_test.automation.coding_agent import AutomationResult
from web_test.automation.entrypoint import (
    AutomationOutcome,
    AutomationStatus,
    automate,
    parse_case,
)

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

PR_URL = HttpUrl("https://github.com/o/r/pull/7")


def test_parse_case_reads_front_matter() -> None:
    case = parse_case(SAMPLE)

    assert case.id == "test-case-0001"
    assert str(case.base_url) == "https://automationexercise.com/"
    assert case.requirement_ids == ["FR-CNT-01"]
    assert case.priority == "High"
    assert case.test_type == "Functional"


def test_parse_case_defaults_optional_fields() -> None:
    case = parse_case("---\nid: test-case-0002\nbase_url: https://example.com\n---\n")

    assert case.requirement_ids == []
    assert case.priority == "Medium"
    assert case.test_type == "Functional"


def test_parse_case_requires_id_and_base_url() -> None:
    with pytest.raises(ValidationError):
        parse_case("---\nid: test-case-0003\n---\n")


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
    pr.open_pull_request.return_value = PR_URL
    suite = MagicMock()
    suite.is_green.return_value = green
    return git, pr, suite


def test_automate_publishes_on_green(tmp_path: Path) -> None:
    case = _write_case(tmp_path)
    agent = MagicMock(return_value=AutomationResult(pr_body="## Summary\n\nbody"))
    git, pr, suite = _deps(files=["tests/a.py"], green=True)

    outcome = automate(case, workspace=tmp_path, agent=agent, git=git, pr=pr, suite=suite)

    assert outcome == AutomationOutcome(AutomationStatus.PUBLISHED, pr_url=PR_URL)
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
