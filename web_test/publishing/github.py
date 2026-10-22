import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, TypedDict, TypeVar

from githubkit import GitHub
from githubkit.exception import GitHubException, RequestFailed, RequestTimeout
from pydantic import BaseModel

T = TypeVar("T")

CheckConclusion = Literal["success", "action_required", "failure"]


class CheckPayload(BaseModel):
    """The check run to publish for one head SHA."""

    name: str = "verify-test-case"
    head_sha: str
    conclusion: CheckConclusion
    title: str
    summary: str
    external_id: str
    status: Literal["completed"] = "completed"


@dataclass(frozen=True)
class PullRequest:
    """The pull request to open, passed between `publish` and `GitHubAdapter`."""

    base: str
    head: str
    title: str
    body: str


class GitHubError(RuntimeError):
    """A GitHub API call failed."""


def _describe(error: GitHubException) -> str:
    if isinstance(error, RequestFailed):
        return (
            f"{error.request.method} {error.request.url} "
            f"-> {error.response.status_code}: {error.response.text[:200]}"
        )
    if isinstance(error, RequestTimeout):
        return f"{error.request.method} {error.request.url} timed out"
    return repr(error)


def _token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required")
    return token


def _repository() -> tuple[str, str]:
    slug = os.environ.get("GITHUB_REPOSITORY", "")
    owner, separator, repo = slug.partition("/")
    if not separator or not owner or not repo or "/" in repo:
        raise RuntimeError("GITHUB_REPOSITORY must be owner/repo")
    return owner, repo


class _CheckBody(TypedDict):
    name: str
    status: Literal["completed"]
    conclusion: CheckConclusion
    completed_at: datetime
    external_id: str


def _check_body(payload: CheckPayload) -> _CheckBody:
    return {
        "name": payload.name,
        "status": "completed",
        "conclusion": payload.conclusion,
        "completed_at": datetime.now(UTC),
        "external_id": payload.external_id,
    }


@dataclass(frozen=True)
class GitHubAdapter:
    client: GitHub
    owner: str
    repo: str

    @classmethod
    def from_env(cls) -> "GitHubAdapter":
        token = _token()
        owner, repo = _repository()
        return cls(client=GitHub(token), owner=owner, repo=repo)

    def _request(self, operation: str, call: Callable[[], T]) -> T:
        try:
            return call()
        except GitHubException as error:
            raise GitHubError(f"GitHub {operation} failed: {_describe(error)}") from error

    def open_pull_request(self, pr: PullRequest) -> None:
        self._request(
            "create pull request",
            lambda: self.client.rest.pulls.create(
                self.owner,
                self.repo,
                title=pr.title,
                head=pr.head,
                base=pr.base,
                body=pr.body,
            ),
        )

    def find_check_run(self, head_sha: str, *, name: str) -> int | None:
        """The existing check run id for `name` on `head_sha`, or `None`."""
        response = self._request(
            "list check runs",
            lambda: self.client.rest.checks.list_for_ref(
                self.owner, self.repo, head_sha, check_name=name
            ),
        )
        runs = response.parsed_data.check_runs
        return int(runs[0].id) if runs else None

    def publish_check(self, payload: CheckPayload) -> None:
        """Create the check run, or update the one already on the head SHA."""
        run_id = self.find_check_run(payload.head_sha, name=payload.name)
        body = _check_body(payload)
        if run_id is None:
            self._request(
                "create check run",
                lambda: self.client.rest.checks.create(
                    self.owner,
                    self.repo,
                    head_sha=payload.head_sha,
                    output={"title": payload.title, "summary": payload.summary},
                    **body,
                ),
            )
        else:
            self._request(
                "update check run",
                lambda: self.client.rest.checks.update(
                    self.owner,
                    self.repo,
                    run_id,
                    output={"title": payload.title, "summary": payload.summary},
                    **body,
                ),
            )
