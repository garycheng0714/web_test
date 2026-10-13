from unittest.mock import MagicMock, call

from pydantic import HttpUrl

from web_test.publishing.github import PullRequest
from web_test.publishing.publish import (
    Publisher,
    branch_name,
    commit_message,
)

CASE_ID = "test-case-0001"
BODY = "## Summary\n\nbody"
BRANCH = "automation/test-case-0001"
PR_URL = HttpUrl("https://github.com/o/r/pull/7")


def test_publisher_commits_and_opens_a_pr() -> None:
    git = MagicMock()
    pr = MagicMock()
    pr.open_pull_request.return_value = PR_URL

    url = Publisher(git=git, pr=pr).publish(
        case_id=CASE_ID, body=BODY, files=["tests/a.py", "pages/p.py"]
    )

    assert url == PR_URL
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
