from pathlib import Path
from unittest.mock import MagicMock

import pytest

from web_test.command import CommandResult
from web_test.publishing.github import GitHub, PullRequest

PR = PullRequest(base="main", head="b", title="t", body="B")


def test_open_pull_request_argv() -> None:
    runner = MagicMock(return_value=CommandResult(0))

    GitHub(runner, Path("/ws")).open_pull_request(PR)

    runner.assert_called_once_with(
        ["gh", "pr", "create", "--base", "main", "--head", "b", "--title", "t", "--body", "B"],
        cwd=Path("/ws"),
    )


def test_failed_pr_raises() -> None:
    runner = MagicMock(return_value=CommandResult(1, stderr="boom"))

    with pytest.raises(RuntimeError):
        GitHub(runner, Path("/ws")).open_pull_request(PR)
