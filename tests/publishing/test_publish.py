from unittest.mock import MagicMock, call

from pydantic import HttpUrl

from web_test.publishing.github import PullRequest
from web_test.publishing.publish import (
    PublishPlan,
    allowed_paths,
    branch_name,
    commit_message,
    plan_publish,
    publish,
)

CASE_ID = "test-case-0001"
BODY = "## Summary\n\nbody"
BRANCH = "automation/test-case-0001"
PR_URL = HttpUrl("https://github.com/o/r/pull/7")


def _git(paths: list[str]) -> MagicMock:
    git = MagicMock()
    git.changed_paths.return_value = list(paths)
    return git


def _suite(*, green: bool) -> MagicMock:
    suite = MagicMock()
    suite.is_green.return_value = green
    return suite


def test_plan_red_suite_is_none() -> None:
    git = _git(["tests/a.py"])

    assert plan_publish(case_id=CASE_ID, body=BODY, git=git, suite=_suite(green=False)) is None
    assert git.method_calls == []


def test_plan_no_changes_is_none() -> None:
    git = _git([])

    assert plan_publish(case_id=CASE_ID, body=BODY, git=git, suite=_suite(green=True)) is None
    assert git.method_calls == [call.changed_paths()]


def test_plan_on_green_keeps_only_permitted_files() -> None:
    git = _git(["tests/a.py", "README.md", "pages/p.py"])

    plan = plan_publish(case_id=CASE_ID, body=BODY, git=git, suite=_suite(green=True))

    assert plan == PublishPlan(case_id=CASE_ID, body=BODY, files=["tests/a.py", "pages/p.py"])


def test_publish_commits_and_opens_a_pr() -> None:
    git = MagicMock()
    pr = MagicMock()
    pr.open_pull_request.return_value = PR_URL
    plan = PublishPlan(case_id=CASE_ID, body=BODY, files=["tests/a.py", "pages/p.py"])

    assert publish(plan, git=git, pr=pr) == PR_URL
    assert git.method_calls == [
        call.set_identity(
            "github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com"
        ),
        call.create_branch(BRANCH),
        call.add(["tests/a.py", "pages/p.py"]),
        call.commit("Add automated tests for test-case-0001"),
        call.push(BRANCH),
    ]
    assert pr.method_calls == [
        call.open_pull_request(
            PullRequest(
                base="main",
                head=BRANCH,
                title="Add automated tests for test-case-0001",
                body=BODY,
            )
        )
    ]


def test_branch_and_commit_use_case_id() -> None:
    assert branch_name(CASE_ID) == "automation/test-case-0001"
    assert commit_message(CASE_ID) == "Add automated tests for test-case-0001"


def test_allowed_paths_keeps_only_guard_permitted() -> None:
    paths = ["tests/a.py", "web_test/x.py", "README.md", "pages/p.py", "tests/n.txt"]

    assert allowed_paths(paths) == ["tests/a.py", "pages/p.py"]
