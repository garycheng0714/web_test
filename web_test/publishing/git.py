from dataclasses import dataclass
from pathlib import Path

from web_test.command import CommandResult, Runner


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


@dataclass(frozen=True)
class Git:
    run: Runner
    workspace: Path

    def _git(self, *args: str) -> CommandResult:
        return self.run(["git", *args], cwd=self.workspace)

    def changed_paths(self) -> list[str]:
        return parse_git_status(self._git("status", "--porcelain").stdout)

    def set_identity(self, name: str, email: str) -> None:
        self._git("config", "user.name", name).check()
        self._git("config", "user.email", email).check()

    def fetch(self, remote: str = "origin") -> None:
        self._git("fetch", remote).check()

    def create_branch(self, branch: str, *, base: str | None = None) -> None:
        args = ["checkout", "-b", branch, *([base] if base else [])]
        self._git(*args).check()

    def add(self, paths: list[str]) -> None:
        self._git("add", "--", *paths).check()

    def commit(self, message: str) -> None:
        self._git("commit", "-m", message).check()

    def push(self, branch: str, remote: str = "origin") -> None:
        self._git("push", "-u", remote, branch).check()
