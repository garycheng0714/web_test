from dataclasses import dataclass
from pathlib import Path

from pydantic import HttpUrl

from web_test.command import Runner


@dataclass(frozen=True)
class PullRequest:
    """The pull request to open, passed between `publish` and `GitHub`."""

    base: str
    head: str
    title: str
    body: str


def _parse_url(stdout: str) -> HttpUrl:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("gh pr create returned no pull request URL")
    return HttpUrl(lines[-1])


@dataclass(frozen=True)
class GitHub:
    run: Runner
    workspace: Path

    def open_pull_request(self, pr: PullRequest) -> HttpUrl:
        """Open `pr` and return the URL `gh pr create` prints."""
        result = self.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                pr.base,
                "--head",
                pr.head,
                "--title",
                pr.title,
                "--body",
                pr.body,
            ],
            cwd=self.workspace,
        ).check()
        return _parse_url(result.stdout)
