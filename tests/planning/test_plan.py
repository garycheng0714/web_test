from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from web_test.planning.entrypoint import PlanStatus, commit_message, main, plan, plan_branch
from web_test.planning.schema import Case

NOW = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def _prd(tmp_path):
    prd = tmp_path / "prd-register.md"
    prd.write_text("# PRD\n", encoding="utf-8")
    return prd


def test_plan_writes_files_and_opens_one_pr(tmp_path):
    agent = MagicMock(return_value=[_case(), _case(test_scenario="Login")])
    git, pr = MagicMock(), MagicMock()

    outcome = plan(
        _prd(tmp_path),
        base_url="https://example.com",
        workspace=tmp_path,
        agent=agent,
        git=git,
        pr=pr,
        now=NOW,
    )

    assert outcome.status is PlanStatus.PLANNED
    assert outcome.files == ["test-case/test-case-0001.md", "test-case/test-case-0002.md"]
    assert (tmp_path / "test-case/test-case-0001.md").exists()
    assert pr.open_pull_request.call_count == 1


def test_plan_opens_no_pr_when_there_are_no_cases(tmp_path):
    agent = MagicMock(return_value=[])
    git, pr = MagicMock(), MagicMock()

    outcome = plan(
        _prd(tmp_path), base_url="https://e.com", workspace=tmp_path, agent=agent, git=git, pr=pr, now=NOW
    )

    assert outcome.status is PlanStatus.NO_CASES
    git.assert_not_called()
    pr.assert_not_called()


def test_plan_reports_a_git_failure(tmp_path):
    agent = MagicMock(return_value=[_case()])
    git, pr = MagicMock(), MagicMock()
    git.commit.side_effect = RuntimeError("boom")

    outcome = plan(
        _prd(tmp_path), base_url="https://e.com", workspace=tmp_path, agent=agent, git=git, pr=pr, now=NOW
    )

    assert outcome.status is PlanStatus.FAILED
    assert outcome.error == "boom"


def test_plan_branch_and_commit_message():
    assert plan_branch("prd-register", NOW) == "plan/prd-register-20261014T120000Z"
    assert commit_message("prd-register.md") == "Add test cases from prd-register.md"


def test_main_requires_prd_and_base_url():
    with pytest.raises(SystemExit):
        main([])


def test_plan_reports_a_missing_prd(tmp_path):
    outcome = plan(
        tmp_path / "missing.md",
        base_url="https://e.com",
        workspace=tmp_path,
        agent=MagicMock(),
        git=MagicMock(),
        pr=MagicMock(),
        now=NOW,
    )

    assert outcome.status is PlanStatus.FAILED
    assert "missing.md" in (outcome.error or "")
