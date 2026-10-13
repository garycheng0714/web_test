import tempfile
from pathlib import Path

import pytest
from pydantic_ai import Agent, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.models.function import FunctionModel
from pydantic_ai_harness.filesystem import FileSystem

from web_test._run import run_sync
from web_test.write_guard import allowed_paths, check_write_permission, write_guard


@pytest.mark.parametrize(
    "path",
    ["tests/test_x.py", "pages/home_page.py", "components/header.py", "tests/conftest.py"],
)
def test_check_write_permission_allows(path: str) -> None:
    assert check_write_permission(path).allow


@pytest.mark.parametrize(
    "path",
    ["/etc/passwd", "../outside.py", "tests/../secret.py", "web_test/coding_agent.py", "main.py", "pyproject.toml", "tests/notes.txt", ""],
)
def test_check_write_permission_rejects(path: str) -> None:
    assert not check_write_permission(path).allow


def test_allowed_paths_keeps_only_permitted() -> None:
    paths = ["tests/a.py", "web_test/x.py", "README.md", "pages/p.py", "tests/n.txt"]

    assert allowed_paths(paths) == ["tests/a.py", "pages/p.py"]


def _write_call(path: str) -> ModelResponse:
    return ModelResponse(
        parts=[ToolCallPart(tool_name="write_file", args={"path": path, "content": "x = 1\n"})]
    )


def _edit_call(path: str, old_text: str, new_text: str) -> ModelResponse:
    return ModelResponse(
        parts=[
            ToolCallPart(
                tool_name="edit_file",
                args={"path": path, "old_text": old_text, "new_text": new_text},
            )
        ]
    )


def _scripted(*responses: ModelResponse) -> FunctionModel:
    remaining = list(responses)

    def respond(messages, info) -> ModelResponse:
        return remaining.pop(0)

    return FunctionModel(respond)


def _run(path: str, first: ModelResponse, *, prewrite: str | None = None) -> str | None:
    with tempfile.TemporaryDirectory() as workspace:
        target = Path(workspace) / path
        target.parent.mkdir(parents=True, exist_ok=True)

        if prewrite is not None:
            target.write_text(prewrite)

        agent = Agent(
            _scripted(first, ModelResponse(parts=[TextPart(content="done")])),
            capabilities=[LocalWorkspace(workspace), FileSystem(), write_guard],
        )

        run_sync(agent.run("do it"))

        return target.read_text() if target.exists() else None


def test_write_guard_allows_a_permitted_path() -> None:
    assert _run("tests/test_generated.py", _write_call("tests/test_generated.py")) is not None


def test_write_guard_rejects_a_disallowed_path() -> None:
    assert _run("web_test/evil.py", _write_call("web_test/evil.py")) is None


def test_write_guard_allows_editing_an_existing_file() -> None:
    text = _run(
        "pages/home_page.py",
        _edit_call("pages/home_page.py", old_text="x = 1", new_text="x = 2"),
        prewrite="x = 1\n",
    )
    assert text == "x = 2\n"


def test_write_guard_rejects_editing_a_disallowed_file() -> None:
    text = _run(
        "web_test/evil.py",
        _edit_call("web_test/evil.py", old_text="x = 1", new_text="x = 2"),
        prewrite="x = 1\n",
    )
    assert text == "x = 1\n"
