from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from web_test.command import Runner


class GitHubProtocol(Protocol):
    def open_pull_request(self, *, base: str, head: str, title: str, body: str) -> None: ...


@dataclass(frozen=True)
class GitHub:
    run: Runner
    workspace: Path

    def open_pull_request(self, *, base: str, head: str, title: str, body: str) -> None:
        self.run(
            ["gh", "pr", "create", "--base", base, "--head", head, "--title", title, "--body", body],
            cwd=self.workspace,
        ).check()
