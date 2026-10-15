from pydantic_ai.models.openai import OpenAIChatModel

from web_test.model import (
    DEFAULT_DESIGN_MODEL,
    DEFAULT_MODEL,
    OPENCODE_GO_BASE_URL,
    resolve_design_model,
    resolve_model,
)


def test_resolve_model_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("WEB_TEST_MODEL", raising=False)
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")

    model = resolve_model()

    assert DEFAULT_MODEL == "openai-chat:kimi-k2.7-code"
    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "kimi-k2.7-code"
    assert OPENCODE_GO_BASE_URL in model.base_url
    # Kimi gets the no-forced-tool-choice workaround.
    assert model.profile.get("supports_forced_tool_choice") is False


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


def test_resolve_design_model_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("WEB_TEST_DESIGN_MODEL", raising=False)
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")

    model = resolve_design_model()

    assert DEFAULT_DESIGN_MODEL == "openai-chat:deepseek-v4.1-flash"
    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "deepseek-v4.1-flash"
    assert OPENCODE_GO_BASE_URL in model.base_url
    # DeepSeek supports forced tool choice, but not while thinking (its default): the flag stays on
    # and only the thinking restriction is set.
    assert model.profile.get("supports_forced_tool_choice", True) is not False
    assert model.profile.get("supports_forced_tool_choice_with_thinking") is False


def test_resolve_design_model_reads_environment(monkeypatch):
    monkeypatch.setenv("WEB_TEST_DESIGN_MODEL", "openai:gpt-5.2")
    assert resolve_design_model() == "openai:gpt-5.2"


def test_design_and_automation_models_are_independent(monkeypatch):
    monkeypatch.setenv("WEB_TEST_MODEL", "openai-chat:kimi-k2.7-code")
    monkeypatch.setenv("WEB_TEST_DESIGN_MODEL", "openai-chat:deepseek-v4.1-flash")
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")

    assert resolve_model().model_name == "kimi-k2.7-code"
    assert resolve_design_model().model_name == "deepseek-v4.1-flash"
