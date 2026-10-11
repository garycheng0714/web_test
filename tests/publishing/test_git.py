from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from web_test.command import CommandResult
from web_test.publishing.git import Git, parse_git_status


def test_changed_paths_runs_status_and_parses() -> None:
    runner = MagicMock(return_value=CommandResult(0, stdout=" M tests/test_a.py\n"))

    assert Git(runner, Path("/ws")).changed_paths() == ["tests/test_a.py"]
    runner.assert_called_once_with(["git", "status", "--porcelain"], cwd=Path("/ws"))


def test_set_identity_configures_name_and_email() -> None:
    runner = MagicMock(return_value=CommandResult(0))

    Git(runner, Path("/ws")).set_identity("bot", "bot@example.com")

    assert runner.call_args_list == [
        call(["git", "config", "user.name", "bot"], cwd=Path("/ws")),
        call(["git", "config", "user.email", "bot@example.com"], cwd=Path("/ws")),
    ]


def test_branch_add_commit_push_argv() -> None:
    runner = MagicMock(return_value=CommandResult(0))
    git = Git(runner, Path("/ws"))

    git.create_branch("b")
    git.add(["tests/a.py", "pages/p.py"])
    git.commit("msg")
    git.push("b")

    assert runner.call_args_list == [
        call(["git", "checkout", "-b", "b"], cwd=Path("/ws")),
        call(["git", "add", "--", "tests/a.py", "pages/p.py"], cwd=Path("/ws")),
        call(["git", "commit", "-m", "msg"], cwd=Path("/ws")),
        call(["git", "push", "-u", "origin", "b"], cwd=Path("/ws")),
    ]


def test_failed_command_raises() -> None:
    runner = MagicMock(return_value=CommandResult(1, stderr="boom"))

    with pytest.raises(RuntimeError):
        Git(runner, Path("/ws")).commit("msg")


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
