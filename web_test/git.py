from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from web_test.process import Runner, run_checked


def parse_git_status(stdout: str) -> list[str]:
    """Parse `git status --porcelain` output into paths."""
    paths = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:]  # drop the two status chars and the space before the path
        if " -> " in path:  # a rename is "R  old -> new"; keep the destination
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip().strip('"'))
    return paths


class GitProtocol(Protocol):
    def changed_paths(self) -> list[str]: ...
    def set_identity(self, name: str, email: str) -> None: ...
    def create_branch(self, branch: str) -> None: ...
    def add(self, paths: list[str]) -> None: ...
    def commit(self, message: str) -> None: ...
    def push(self, branch: str) -> None: ...


@dataclass(frozen=True)
class Git:
    run: Runner
    workspace: Path

    def changed_paths(self) -> list[str]:
        stdout = self.run(["git", "status", "--porcelain"], cwd=self.workspace).stdout
        return parse_git_status(stdout)

    def set_identity(self, name: str, email: str) -> None:
        run_checked(self.run, ["git", "config", "user.name", name], cwd=self.workspace)
        run_checked(self.run, ["git", "config", "user.email", email], cwd=self.workspace)

    def create_branch(self, branch: str) -> None:
        run_checked(self.run, ["git", "checkout", "-b", branch], cwd=self.workspace)

    def add(self, paths: list[str]) -> None:
        run_checked(self.run, ["git", "add", "--", *paths], cwd=self.workspace)

    def commit(self, message: str) -> None:
        run_checked(self.run, ["git", "commit", "-m", message], cwd=self.workspace)

    def push(self, branch: str, remote: str = "origin") -> None:
        run_checked(self.run, ["git", "push", "-u", remote, branch], cwd=self.workspace)
