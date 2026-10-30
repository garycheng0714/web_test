from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest
from githubkit import GitHub
from githubkit.exception import GitHubException, RequestFailed, RequestTimeout
from githubkit.response import Response as GitHubResponse

from web_test.publishing.github import (
    CheckPayload,
    GitHubAdapter,
    GitHubError,
    PullRequest,
)

PR = PullRequest(base="main", head="b", title="t", body="B")
CHECK = CheckPayload(
    head_sha="abc",
    conclusion="success",
    title="Test Case verification: PASS",
    summary="## Jev review",
    external_id="key",
)


def _adapter(client: MagicMock) -> GitHubAdapter:
    return GitHubAdapter(client=client, owner="o", repo="r")


def _check_runs(*runs: int) -> SimpleNamespace:
    return SimpleNamespace(
        parsed_data=SimpleNamespace(check_runs=[SimpleNamespace(id=run_id) for run_id in runs])
    )


CHECK_RUNS_URL = "https://api.github.com/repos/o/r/check-runs"


def _request_failed(status: int, text: str) -> RequestFailed:
    request = httpx.Request("GET", CHECK_RUNS_URL)
    raw = httpx.Response(status, text=text, request=request)
    return RequestFailed(GitHubResponse(raw, type(None)))


def test_open_pull_request_uses_the_sdk() -> None:
    client = MagicMock()

    _adapter(client).open_pull_request(PR)

    client.rest.pulls.create.assert_called_once_with(
        "o", "r", title="t", head="b", base="main", body="B"
    )


def test_find_check_run_returns_the_id() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.return_value = _check_runs(42)

    found = _adapter(client).find_check_run("abc", name="verify-test-case")

    assert found == 42
    client.rest.checks.list_for_ref.assert_called_once_with(
        "o", "r", "abc", check_name="verify-test-case"
    )


def test_find_check_run_returns_none_when_absent() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.return_value = _check_runs()

    assert _adapter(client).find_check_run("abc", name="verify-test-case") is None


def test_publish_check_creates_when_absent() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.return_value = _check_runs()

    _adapter(client).publish_check(CHECK)

    client.rest.checks.create.assert_called_once()
    args, kwargs = client.rest.checks.create.call_args
    assert args == ("o", "r")
    assert kwargs["name"] == "verify-test-case"
    assert kwargs["head_sha"] == "abc"
    assert kwargs["status"] == "completed"
    assert kwargs["conclusion"] == "success"
    assert kwargs["external_id"] == "key"
    assert kwargs["output"] == {
        "title": "Test Case verification: PASS",
        "summary": "## Jev review",
    }
    completed_at = kwargs["completed_at"]
    assert isinstance(completed_at, datetime)
    assert completed_at.utcoffset().total_seconds() == 0
    assert completed_at.tzinfo is UTC


def test_publish_check_updates_an_existing_run() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.return_value = _check_runs(7)

    _adapter(client).publish_check(CHECK)

    client.rest.checks.update.assert_called_once()
    args, kwargs = client.rest.checks.update.call_args
    assert args == ("o", "r", 7)
    assert kwargs["conclusion"] == "success"
    assert kwargs["external_id"] == "key"


def test_a_github_error_is_wrapped_with_the_operation() -> None:
    client = MagicMock()
    cause = GitHubException("boom")
    client.rest.checks.list_for_ref.side_effect = cause

    with pytest.raises(GitHubError, match="GitHub list check runs failed"):
        _adapter(client).find_check_run("abc", name="verify-test-case")

    assert client.rest.checks.list_for_ref.call_args is not None


def test_a_github_error_keeps_its_cause() -> None:
    client = MagicMock()
    cause = GitHubException("boom")
    client.rest.checks.list_for_ref.side_effect = cause

    with pytest.raises(GitHubError) as raised:
        _adapter(client).find_check_run("abc", name="verify-test-case")

    assert raised.value.__cause__ is cause


def test_a_status_failure_reports_method_url_status_and_truncated_text() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.side_effect = _request_failed(500, "boom" * 100)

    with pytest.raises(GitHubError) as raised:
        _adapter(client).find_check_run("abc", name="verify-test-case")

    message = str(raised.value)
    assert f"GitHub list check runs failed: GET {CHECK_RUNS_URL} -> 500: boom" in message
    assert message.endswith("boom" * 50)


def test_a_timeout_reports_the_method_and_url() -> None:
    client = MagicMock()
    client.rest.checks.list_for_ref.side_effect = RequestTimeout(
        httpx.TimeoutException("timed out", request=httpx.Request("GET", CHECK_RUNS_URL))
    )

    with pytest.raises(GitHubError) as raised:
        _adapter(client).find_check_run("abc", name="verify-test-case")

    assert str(raised.value) == f"GitHub list check runs failed: GET {CHECK_RUNS_URL} timed out"


def test_from_env_reads_the_token_and_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

    adapter = GitHubAdapter.from_env()

    assert isinstance(adapter.client, GitHub)
    assert adapter.owner == "owner"
    assert adapter.repo == "repo"


def test_from_env_falls_back_to_github_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

    assert GitHubAdapter.from_env().owner == "owner"


def test_from_env_requires_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

    with pytest.raises(RuntimeError, match="GH_TOKEN or GITHUB_TOKEN"):
        GitHubAdapter.from_env()


def test_from_env_requires_a_valid_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    with pytest.raises(RuntimeError, match="GITHUB_REPOSITORY"):
        GitHubAdapter.from_env()
