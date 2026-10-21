import os
import uuid

from openai import AsyncOpenAI
from pydantic_ai import ModelProfile
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.openai import OpenAIProvider

OPENCODE_GO_BASE_URL = "https://opencode.ai/inference/go/v1"
DEFAULT_MODEL = "openai-chat:kimi-k2.7-code"
DEFAULT_DESIGN_MODEL = "openai-chat:deepseek-v4.1-flash"


def _profile(model_name: str) -> ModelProfile | None:
    if model_name.startswith("kimi-"):
        # Kimi always thinks and its reasoning can't be turned off, so a forced tool choice is never
        # usable; claim none so pydantic-ai uses `auto` (matches pydantic-ai's Moonshot provider).
        return ModelProfile(supports_forced_tool_choice=False)
    if model_name.startswith("deepseek-"):
        # DeepSeek supports forced tool choice, but not while thinking — and thinking is on by default.
        # Keep `supports_forced_tool_choice` on and mark only the thinking restriction, so pydantic-ai
        # falls back to `auto` while thinking. With tools, DeepSeek requires each turn's
        # `reasoning_content` to be passed back, or the next request 400s.
        return OpenAIModelProfile(
            supports_thinking=True,
            thinking_enabled_by_default=True,
            supports_forced_tool_choice_with_thinking=False,
            openai_chat_thinking_field="reasoning_content",
            openai_chat_send_back_thinking_parts="field",
        )
    return None


def _resolve(name: str) -> Model | str:
    if not name.startswith("openai-chat:"):
        return name
    model_name = name.removeprefix("openai-chat:")
    # OpenCode Go's Chat Completions endpoint needs a stable per-run session (routing and prompt
    # caching) and a distinct user agent, and it keys off OPENCODE_API_KEY, not the ambient
    # OPENAI_API_KEY. Build the client by hand because OpenAIProvider does not expose headers.
    client = AsyncOpenAI(
        base_url=OPENCODE_GO_BASE_URL,
        api_key=os.environ.get("OPENCODE_API_KEY") or "api-key-not-set",
        default_headers={
            "x-opencode-session": uuid.uuid4().hex,
            "User-Agent": "web-test/0.1.0",
        },
    )
    return OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(openai_client=client),
        profile=_profile(model_name),
    )


def resolve_model() -> Model | str:
    """The automation/coding-agent model."""
    return _resolve(os.environ.get("WEB_TEST_MODEL") or DEFAULT_MODEL)


def resolve_design_model() -> Model | str:
    """The designer model (PRD → test cases)."""
    return _resolve(os.environ.get("WEB_TEST_DESIGN_MODEL") or DEFAULT_DESIGN_MODEL)
