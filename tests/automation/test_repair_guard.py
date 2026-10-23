import pytest

from web_test.automation.repair_guard import (
    MAX_PYTEST_RUNS,
    RepairBudgetExceeded,
    count_pytest_run,
)


def test_pytest_run_is_counted() -> None:
    assert count_pytest_run("uv run pytest tests/a.py -q", 0) == 1


def test_non_pytest_command_is_ignored() -> None:
    assert count_pytest_run("uv run ruff check", 3) == 3


def test_exceeding_the_bound_raises() -> None:
    with pytest.raises(RepairBudgetExceeded):
        count_pytest_run("uv run pytest tests/a.py -q", MAX_PYTEST_RUNS)


from types import SimpleNamespace

from web_test._run import run_sync
from web_test.automation.repair_guard import (
    AutomationDeps,
    _capture_shell_result,
    _enforce_repair_budget,
)


def test_shell_calls_are_traced_and_pytest_runs_counted() -> None:
    deps = AutomationDeps()
    ctx = SimpleNamespace(deps=deps, usage=None)

    run_sync(
        _enforce_repair_budget(
            ctx,
            call=None,
            tool_def=None,
            args={"command": "uv run pytest -q"},
        )
    )

    assert deps.pytest_runs == 1
    assert deps.tool_trace == ["-> uv run pytest -q"]


def test_pytest_output_is_captured_for_the_caller() -> None:
    deps = AutomationDeps()
    ctx = SimpleNamespace(deps=deps, usage=None)

    result = run_sync(
        _capture_shell_result(
            ctx,
            call=None,
            tool_def=None,
            args={"command": "uv run pytest -q"},
            result="1 failed",
        )
    )

    assert result == "1 failed"
    assert deps.last_pytest_output == "1 failed"
    assert any("1 failed" in line for line in deps.tool_trace)
