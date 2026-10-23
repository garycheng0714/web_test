import os
from dataclasses import dataclass, field

from pydantic_ai import RunContext
from pydantic_ai.capabilities import ValidatedToolArgs
from pydantic_ai.capabilities.hooks import Hooks

from web_test.observability import log_usage_value

# How many times the agent may fix a failing run before it is stopped (overridable for cost control).
REPAIR_ATTEMPTS = int(os.environ.get("WEB_TEST_REPAIR_ATTEMPTS", "4"))
# The initial verify run plus the repair attempts; enforced below, not just instructed.
MAX_PYTEST_RUNS = REPAIR_ATTEMPTS + 1
# Keep the captured trace bounded; the deciding pytest output is kept separately.
TRACE_OUTPUT_LIMIT = 4000


@dataclass
class AutomationDeps:
    """Per-run state the repair guard reads and writes."""

    pytest_runs: int = 0
    last_pytest_output: str | None = None
    tool_trace: list[str] = field(default_factory=list)


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
    command = str(args.get("command", ""))
    ctx.deps.tool_trace.append(f"-> {command}")
    try:
        ctx.deps.pytest_runs = count_pytest_run(command, ctx.deps.pytest_runs)
    except RepairBudgetExceeded:
        log_usage_value(ctx.usage)
        raise
    return args


@repair_guard.on.after_tool_execute(tools=["shell"])
async def _capture_shell_result(
    ctx: RunContext[AutomationDeps],
    *,
    call: object,
    tool_def: object,
    args: ValidatedToolArgs,
    result: object,
) -> object:
    command = str(args.get("command", ""))
    output = str(result)
    ctx.deps.tool_trace.append(f"<- {command}: {output[:TRACE_OUTPUT_LIMIT]}")
    if "pytest" in command:
        ctx.deps.last_pytest_output = output
    return result
