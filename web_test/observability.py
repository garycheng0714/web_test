import os
import sys
from collections.abc import Iterable
from typing import Any

import logfire
from pydantic_ai.messages import ToolCallPart, ToolReturnPart

_CLIP = 160


def configure_observability() -> None:
    """Turn on pydantic-ai telemetry.

    Spans go to Logfire when `LOGFIRE_TOKEN` is set, and to the console otherwise, so
    a local run shows each model request's token usage (input/output/cached) without an
    account.
    """
    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()


def log_usage(result: Any) -> None:
    """Print the run's token usage and cost when `WEB_TEST_USAGE` is set."""
    log_usage_value(result.usage)


def log_usage_value(usage: Any) -> None:
    """Print a usage object when `WEB_TEST_USAGE` is set (also usable mid-run)."""
    if os.environ.get("WEB_TEST_USAGE"):
        print(f"usage: {usage}", file=sys.stderr)


def log_captured_trace(lines: Iterable[str]) -> None:
    """Print already-captured tool calls when the run itself did not return a result."""
    if not os.environ.get("WEB_TEST_TRACE"):
        return
    for line in lines:
        print(line, file=sys.stderr)


def log_trace(result: Any) -> None:
    """Print the run's tool calls and per-request usage when `WEB_TEST_TRACE` is set."""
    if not os.environ.get("WEB_TEST_TRACE"):
        return
    for message in result.all_messages():
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart):
                print(f"  -> {part.tool_name} {_clip(str(part.args))}", file=sys.stderr)
            elif isinstance(part, ToolReturnPart):
                print(f"  <- {part.tool_name}: {_clip(str(part.content))}", file=sys.stderr)
        usage = getattr(message, "usage", None)
        if usage is not None:
            print(
                f"  [usage] in={usage.input_tokens} out={usage.output_tokens} "
                f"cache_read={usage.cache_read_tokens}",
                file=sys.stderr,
            )


def _clip(text: str) -> str:
    return text if len(text) <= _CLIP else f"{text[:_CLIP]}…"
