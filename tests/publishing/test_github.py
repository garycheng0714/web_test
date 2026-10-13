from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import HttpUrl

from web_test.command import CommandResult
from web_test.publishing.github import GitHub, PullRequest

PR = PullRequest(base="main", head="b", title="t", body="B")


def test_open_pull_request_argv_and_url() -> None:
    runner = MagicMock(return_value=CommandResult(0, stdout="https://github.com/o/r/pull/7\n"))

    url = GitHub(runner, Path("/ws")).open_pull_request(PR)

    runner.assert_called_once_with(
        ["gh", "pr", "create", "--base", "main", "--head", "b", "--title", "t", "--body", "B"],
        cwd=Path("/ws"),
    )
    assert url == HttpUrl("https://github.com/o/r/pull/7")


def test_failed_pr_raises() -> None:
    runner = MagicMock(return_value=CommandResult(1, stderr="boom"))

    with pytest.raises(RuntimeError):
        GitHub(runner, Path("/ws")).open_pull_request(PR)


def test_missing_url_raises() -> None:
    runner = MagicMock(return_value=CommandResult(0, stdout="\n"))

    with pytest.raises(RuntimeError):
        GitHub(runner, Path("/ws")).open_pull_request(PR)
