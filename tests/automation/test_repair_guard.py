from collections.abc import Coroutine
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic_ai import RunContext
from pydantic_ai.capabilities import ValidatedToolArgs
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import ToolDefinition

from web_test._run import run_sync
from web_test.automation.repair_guard import (
    MAX_PYTEST_RUNS,
    AutomationDeps,
    RepairBudgetExceeded,
    _capture_shell_result,
    _enforce_repair_budget,
    count_pytest_run,
)


def test_pytest_run_is_counted() -> None:
    assert count_pytest_run("uv run pytest tests/a.py -q", 0) == 1


def test_non_pytest_command_is_ignored() -> None:
    assert count_pytest_run("uv run ruff check", 3) == 3


def test_exceeding_the_bound_raises() -> None:
    with pytest.raises(RepairBudgetExceeded):
        count_pytest_run("uv run pytest tests/a.py -q", MAX_PYTEST_RUNS)


def _ctx(deps: AutomationDeps) -> RunContext[AutomationDeps]:
    """The handlers only read `ctx.deps`; a real RunContext needs a model and a prompt."""
    return cast(RunContext[AutomationDeps], SimpleNamespace(deps=deps, usage=None))


def _shell(command: str) -> tuple[ToolCallPart, ToolDefinition]:
    return (
        ToolCallPart(tool_name="shell", args={"command": command}),
        ToolDefinition(name="shell"),
    )


def test_shell_calls_are_traced_and_pytest_runs_counted() -> None:
    deps = AutomationDeps()
    call, tool_def = _shell("uv run pytest -q")

    # The hook decorator's overloads admit a sync handler too; these two are async.
    run_sync(
        cast(
            Coroutine[Any, Any, ValidatedToolArgs],
            _enforce_repair_budget(
                _ctx(deps),
                call=call,
                tool_def=tool_def,
                args={"command": "uv run pytest -q"},
            ),
        )
    )

    assert deps.pytest_runs == 1
    assert deps.tool_trace == ["-> uv run pytest -q"]


def test_pytest_output_is_captured_for_the_caller() -> None:
    deps = AutomationDeps()
    call, tool_def = _shell("uv run pytest -q")

    result = run_sync(
        cast(
            Coroutine[Any, Any, object],
            _capture_shell_result(
                _ctx(deps),
                call=call,
                tool_def=tool_def,
                args={"command": "uv run pytest -q"},
                result="1 failed",
            ),
        )
    )

    assert result == "1 failed"
    assert deps.last_pytest_output == "1 failed"
    assert any("1 failed" in line for line in deps.tool_trace)
