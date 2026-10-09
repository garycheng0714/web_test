from datetime import date

from web_test import write_guard
from web_test.paths import FEATURE
from web_test.publishing.git import GitProtocol
from web_test.publishing.github import GitHubProtocol
from web_test.publishing.suite import SuiteProtocol

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BASE_BRANCH = "main"


def allowed_paths(paths: list[str]) -> list[str]:
    """The subset the write guard permits."""
    return [path for path in paths if write_guard.check_write_permission(path).allow]


def branch_name(feature: str, today: date) -> str:
    return f"automation/{feature}-{today.isoformat()}"


def commit_message(case_ids: list[str]) -> str:
    return "Add automated tests for " + ", ".join(case_ids)


def publish(
    *,
    case_ids: list[str],
    body: str,
    git: GitProtocol,
    pr: GitHubProtocol,
    suite: SuiteProtocol,
    today: date | None = None,
) -> str | None:
    """Publish the run's changes as a PR once the suite is green.

    Returns the branch name when a PR was opened, else `None`. `body` is the
    PR body produced elsewhere; this function never generates it.
    """
    if not suite.is_green():
        return None

    files = allowed_paths(git.changed_paths())
    if not files:
        return None

    branch = branch_name(FEATURE, today or date.today())
    message = commit_message(case_ids)

    git.set_identity(BOT_NAME, BOT_EMAIL)
    git.create_branch(branch)
    git.add(files)
    git.commit(message)
    git.push(branch)
    pr.open_pull_request(base=BASE_BRANCH, head=branch, title=message, body=body)
    return branch
