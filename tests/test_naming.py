from datetime import UTC, datetime

from web_test.naming import branch_for, run_token

NOW = datetime(2026, 10, 14, 12, 0, 0, tzinfo=UTC)


def test_run_token_uses_the_run_id_and_attempt(monkeypatch):
    monkeypatch.setenv("WEB_TEST_RUN_ID", "123")
    monkeypatch.setenv("WEB_TEST_RUN_ATTEMPT", "2")

    assert run_token() == "123-2"


def test_run_token_uses_the_run_id_alone_without_an_attempt(monkeypatch):
    monkeypatch.setenv("WEB_TEST_RUN_ID", "123")
    monkeypatch.delenv("WEB_TEST_RUN_ATTEMPT", raising=False)

    assert run_token() == "123"


def test_run_token_falls_back_to_a_utc_timestamp(monkeypatch):
    monkeypatch.delenv("WEB_TEST_RUN_ID", raising=False)
    monkeypatch.delenv("WEB_TEST_RUN_ATTEMPT", raising=False)

    assert run_token(NOW) == "20261014T120000Z"


def test_branch_for_uses_the_kind_and_identifier():
    assert branch_for("plan", "register-login", "123-2") == "plan/register-login-123-2"
    assert branch_for("automation", "test-case-0001", "9") == "automation/test-case-0001-9"
