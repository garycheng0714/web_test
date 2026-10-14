from pydantic_ai.models.openai import OpenAIChatModel

from web_test.model import DEFAULT_MODEL, OPENCODE_GO_BASE_URL, resolve_model


def test_resolve_model_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("WEB_TEST_MODEL", raising=False)
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")

    model = resolve_model()

    assert DEFAULT_MODEL == "openai-chat:kimi-k2.7-code"
    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "kimi-k2.7-code"
    assert OPENCODE_GO_BASE_URL in model.base_url


def test_resolve_model_reads_environment(monkeypatch):
    monkeypatch.setenv("WEB_TEST_MODEL", "openai:gpt-5.2")
    assert resolve_model() == "openai:gpt-5.2"


def test_resolve_model_builds_the_opencode_go_provider(monkeypatch):
    monkeypatch.setenv("WEB_TEST_MODEL", "openai-chat:kimi-k2.7-code")
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")

    model = resolve_model()

    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "kimi-k2.7-code"
    assert OPENCODE_GO_BASE_URL in model.base_url
