from pathlib import Path

import pytest

from web_test.process import CommandResult
from web_test.publishing.git import Git, parse_git_status


class FakeRunner:
    def __init__(self, *, stdout: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], *, cwd: object = None) -> CommandResult:
        self.calls.append(list(args))
        stderr = "boom" if self.returncode else ""
        return CommandResult(self.returncode, stdout=self.stdout, stderr=stderr)

    def git(self) -> Git:
        return Git(self, Path("/ws"))


def test_changed_paths_runs_status_and_parses() -> None:
    runner = FakeRunner(stdout=" M tests/test_a.py\n")

    assert runner.git().changed_paths() == ["tests/test_a.py"]
    assert runner.calls == [["git", "status", "--porcelain"]]


def test_set_identity_configures_name_and_email() -> None:
    runner = FakeRunner()

    runner.git().set_identity("bot", "bot@example.com")

    assert runner.calls == [
        ["git", "config", "user.name", "bot"],
        ["git", "config", "user.email", "bot@example.com"],
    ]


def test_branch_add_commit_push_argv() -> None:
    runner = FakeRunner()
    git = runner.git()

    git.create_branch("b")
    git.add(["tests/a.py", "pages/p.py"])
    git.commit("msg")
    git.push("b")

    assert runner.calls == [
        ["git", "checkout", "-b", "b"],
        ["git", "add", "--", "tests/a.py", "pages/p.py"],
        ["git", "commit", "-m", "msg"],
        ["git", "push", "-u", "origin", "b"],
    ]


def test_failed_command_raises() -> None:
    runner = FakeRunner(returncode=1)

    with pytest.raises(RuntimeError):
        runner.git().commit("msg")


def test_parse_git_status_handles_status_chars_renames_and_quotes() -> None:
    stdout = (
        " M tests/test_a.py\n"
        "?? pages/p.py\n"
        "R  pages/old.py -> components/new.py\n"
        '?? "tests/a b.py"\n'
    )

    assert parse_git_status(stdout) == [
        "tests/test_a.py",
        "pages/p.py",
        "components/new.py",
        "tests/a b.py",
    ]
