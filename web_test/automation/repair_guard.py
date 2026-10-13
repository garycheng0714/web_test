import os
from dataclasses import dataclass

from pydantic_ai import RunContext
from pydantic_ai.capabilities import ValidatedToolArgs
from pydantic_ai.capabilities.hooks import Hooks

from web_test.observability import log_usage_value

# How many times the agent may fix a failing run before it is stopped (overridable for cost control).
REPAIR_ATTEMPTS = int(os.environ.get("WEB_TEST_REPAIR_ATTEMPTS", "4"))
# The initial verify run plus the repair attempts; enforced below, not just instructed.
MAX_PYTEST_RUNS = REPAIR_ATTEMPTS + 1


@dataclass
class AutomationDeps:
    """Per-run state the repair guard reads and writes."""

    pytest_runs: int = 0


class RepairBudgetExceeded(Exception):
    """Raised to end a run that kept re-running the suite past its repair bound."""


def count_pytest_run(command: str, runs: int) -> int:
    """Return the new pytest-run count, or raise once it exceeds the repair bound."""
    if "pytest" not in command:
        return runs
    runs += 1
    if runs > MAX_PYTEST_RUNS:
        raise RepairBudgetExceeded(f"stopped after {MAX_PYTEST_RUNS} pytest runs")
    return runs


repair_guard = Hooks(id="repair_guard")


@repair_guard.on.before_tool_execute(tools=["shell"])
async def _enforce_repair_budget(
    ctx: RunContext[AutomationDeps],
    *,
    call: object,
    tool_def: object,
    args: ValidatedToolArgs,
) -> ValidatedToolArgs:
    try:
        ctx.deps.pytest_runs = count_pytest_run(str(args.get("command", "")), ctx.deps.pytest_runs)
    except RepairBudgetExceeded:
        log_usage_value(ctx.usage)
        raise
    return args
