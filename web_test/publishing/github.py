from dataclasses import dataclass
from pathlib import Path

from web_test.command import Runner


@dataclass(frozen=True)
class PullRequest:
    """The pull request to open, passed between `publish` and `GitHub`."""

    base: str
    head: str
    title: str
    body: str


@dataclass(frozen=True)
class GitHub:
    run: Runner
    workspace: Path

    def open_pull_request(self, pr: PullRequest) -> None:
        self.run(
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
