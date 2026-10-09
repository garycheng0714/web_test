from pathlib import Path

import pytest

from web_test.process import CommandResult
from web_test.publishing.github import GitHub


class FakeRunner:
    def __init__(self, *, returncode: int = 0) -> None:
        self.returncode = returncode
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], *, cwd: object = None) -> CommandResult:
        self.calls.append(list(args))
        stderr = "boom" if self.returncode else ""
        return CommandResult(self.returncode, stderr=stderr)


def test_open_pull_request_argv() -> None:
    runner = FakeRunner()

    GitHub(runner, Path("/ws")).open_pull_request(base="main", head="b", title="t", body="B")

    assert runner.calls == [
        ["gh", "pr", "create", "--base", "main", "--head", "b", "--title", "t", "--body", "B"]
    ]


def test_failed_pr_raises() -> None:
    runner = FakeRunner(returncode=1)

    with pytest.raises(RuntimeError):
        GitHub(runner, Path("/ws")).open_pull_request(base="main", head="b", title="t", body="B")
