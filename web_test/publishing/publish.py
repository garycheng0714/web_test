from pydantic import HttpUrl

from web_test import write_guard
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub, PullRequest

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BASE_BRANCH = "main"


def allowed_paths(paths: list[str]) -> list[str]:
    """The subset the write guard permits."""
    return [path for path in paths if write_guard.check_write_permission(path).allow]


def branch_name(case_id: str) -> str:
    return f"automation/{case_id}"


def commit_message(case_id: str) -> str:
    return f"Add automated tests for {case_id}"


class Publisher:
    """Commits a case's files on a branch and opens one PR."""

    def __init__(self, *, git: Git, pr: GitHub) -> None:
        self.git = git
        self.pr = pr

    def publish(self, *, case_id: str, body: str, files: list[str]) -> HttpUrl:
        branch = branch_name(case_id)
        message = commit_message(case_id)

        self.git.set_identity(BOT_NAME, BOT_EMAIL)
        self.git.create_branch(branch)
        self.git.add(files)
        self.git.commit(message)
        self.git.push(branch)
        return self.pr.open_pull_request(
            PullRequest(base=BASE_BRANCH, head=branch, title=message, body=body)
        )
