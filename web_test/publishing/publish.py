from dataclasses import dataclass

from pydantic import HttpUrl

from web_test import write_guard
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub, PullRequest
from web_test.publishing.suite import Suite

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BASE_BRANCH = "main"


@dataclass(frozen=True)
class PublishPlan:
    """What to publish for one case: the permitted changed files and the PR body."""

    case_id: str
    body: str
    files: list[str]


def allowed_paths(paths: list[str]) -> list[str]:
    """The subset the write guard permits."""
    return [path for path in paths if write_guard.check_write_permission(path).allow]


def branch_name(case_id: str) -> str:
    return f"automation/{case_id}"


def commit_message(case_id: str) -> str:
    return f"Add automated tests for {case_id}"


def plan_publish(*, case_id: str, body: str, git: Git, suite: Suite) -> PublishPlan | None:
    """Decide whether and what to publish.

    Returns `None` when the suite is red or nothing permitted changed.
    """
    if not suite.is_green():
        return None

    files = allowed_paths(git.changed_paths())
    if not files:
        return None

    return PublishPlan(case_id=case_id, body=body, files=files)


def publish(plan: PublishPlan, *, git: Git, pr: GitHub) -> HttpUrl:
    """Commit the plan's files on a branch and open one PR, returning its URL."""
    branch = branch_name(plan.case_id)
    message = commit_message(plan.case_id)

    git.set_identity(BOT_NAME, BOT_EMAIL)
    git.create_branch(branch)
    git.add(plan.files)
    git.commit(message)
    git.push(branch)
    return pr.open_pull_request(
        PullRequest(base=BASE_BRANCH, head=branch, title=message, body=plan.body)
    )
