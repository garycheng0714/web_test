from web_test.naming import branch_for
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub, PullRequest

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BASE_BRANCH = "main"


def branch_name(case_id: str, token: str) -> str:
    return branch_for("automation", case_id, token)


def commit_message(case_id: str) -> str:
    return f"Add automated tests for {case_id}"


class Publisher:
    """Commits a case's files on a branch and opens one PR."""

    def __init__(self, *, git: Git, pr: GitHub) -> None:
        self.git = git
        self.pr = pr

    def publish(self, *, case_id: str, body: str, files: list[str], token: str) -> None:
        branch = branch_name(case_id, token)
        message = commit_message(case_id)

        self.git.set_identity(BOT_NAME, BOT_EMAIL)
        self.git.create_branch(branch)
        self.git.add(files)
        self.git.commit(message)
        self.git.push(branch)
        self.pr.open_pull_request(
            PullRequest(base=BASE_BRANCH, head=branch, title=message, body=body)
        )
