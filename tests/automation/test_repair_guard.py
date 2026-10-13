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
