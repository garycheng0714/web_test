import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from web_test.command import CommandResult
from web_test.publishing.github import CheckConclusion, CheckPayload, GitHub, PullRequest

PR = PullRequest(base="main", head="b", title="t", body="B")
CHECK = CheckPayload(
    head_sha="abc",
    conclusion=CheckConclusion.SUCCESS,
    title="Test Case verification: PASS",
    summary="## Jev review",
    external_id="key",
)


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


def test_find_check_run_returns_the_id() -> None:
    runner = MagicMock(return_value=CommandResult(0, stdout='{"check_runs": [{"id": 42}]}'))

    found = GitHub(runner, Path("/ws")).find_check_run(
        "abc", repo="o/r", name="verify-test-case"
    )

    assert found == 42
    runner.assert_called_once_with(
        ["gh", "api", "repos/o/r/commits/abc/check-runs?check_name=verify-test-case"],
        cwd=Path("/ws"),
    )


def test_find_check_run_returns_none_when_absent() -> None:
    runner = MagicMock(return_value=CommandResult(0, stdout='{"check_runs": []}'))

    assert GitHub(runner, Path("/ws")).find_check_run(
        "abc", repo="o/r", name="verify-test-case"
    ) is None


def test_publish_check_posts_when_absent() -> None:
    calls: list[list[str]] = []
    bodies: list[dict[str, object]] = []

    def runner(args: list[str], *, cwd: Path | None = None) -> CommandResult:
        calls.append(args)
        if "--input" in args:
            path = Path(args[args.index("--input") + 1])
            bodies.append(json.loads(path.read_text(encoding="utf-8")))
            return CommandResult(0)
        return CommandResult(0, stdout='{"check_runs": []}')

    GitHub(runner, Path("/ws")).publish_check(CHECK, repo="o/r")

    assert bodies == [
        {
            "name": "verify-test-case",
            "head_sha": "abc",
            "status": "completed",
            "conclusion": "success",
            "output": {"title": "Test Case verification: PASS", "summary": "## Jev review"},
            "external_id": "key",
        }
    ]
    assert calls[1][calls[1].index("--method") + 1] == "POST"
    assert "repos/o/r/check-runs" in calls[1]
    assert not any("check-runs/" in arg for arg in calls[1])


def test_publish_check_patches_an_existing_run() -> None:
    calls: list[list[str]] = []

    def runner(args: list[str], *, cwd: Path | None = None) -> CommandResult:
        calls.append(args)
        if "--input" in args:
            return CommandResult(0)
        return CommandResult(0, stdout='{"check_runs": [{"id": 7}]}')

    GitHub(runner, Path("/ws")).publish_check(CHECK, repo="o/r")

    assert calls[1][calls[1].index("--method") + 1] == "PATCH"
    assert "repos/o/r/check-runs/7" in calls[1]


def test_failed_publish_raises() -> None:
    runner = MagicMock(return_value=CommandResult(1, stderr="boom"))

    with pytest.raises(RuntimeError):
        GitHub(runner, Path("/ws")).publish_check(CHECK, repo="o/r")
