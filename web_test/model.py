import os
import uuid

from openai import AsyncOpenAI
from pydantic_ai import ModelProfile
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

OPENCODE_GO_BASE_URL = "https://opencode.ai/inference/go/v1"
DEFAULT_MODEL = "openai-chat:kimi-k2.7-code"


def resolve_model() -> Model | str:
    name = os.environ.get("WEB_TEST_MODEL") or DEFAULT_MODEL
    if name.startswith("openai-chat:"):
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
            name.removeprefix("openai-chat:"),
            provider=OpenAIProvider(openai_client=client),
            # Kimi K2.7 Code always thinks, and its upstream rejects `tool_choice: required` (which
            # pydantic-ai otherwise sends to force the output tool). Claim no forcing so it uses `auto`.
            profile=ModelProfile(supports_forced_tool_choice=False),
        )
    return name
