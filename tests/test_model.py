from web_test.model import DEFAULT_MODEL, resolve_model


def test_resolve_model_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("WEB_TEST_MODEL", raising=False)
    assert resolve_model() == DEFAULT_MODEL


def test_resolve_model_reads_environment(monkeypatch):
    monkeypatch.setenv("WEB_TEST_MODEL", "openai:gpt-5.2")
    assert resolve_model() == "openai:gpt-5.2"
