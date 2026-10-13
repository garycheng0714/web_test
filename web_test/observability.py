import os
import sys
from typing import Any

import logfire


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
    if os.environ.get("WEB_TEST_USAGE"):
        print(f"usage: {result.usage}", file=sys.stderr)

