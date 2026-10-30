import tempfile
from pathlib import Path

import pytest
from pydantic_ai import Agent, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.models.function import FunctionModel
from pydantic_ai_harness.filesystem import FileSystem

from web_test._run import run_sync
from web_test.write_guard import (
    allowed_paths,
    check_write_permission,
    resolve_workspace_path,
    write_guard,
)


@pytest.mark.parametrize(
    "path",
    ["tests/test_x.py", "pages/home_page.py", "components/header.py", "tests/conftest.py"],
)
def test_check_write_permission_allows(path: str) -> None:
    assert check_write_permission(path).allow


@pytest.mark.parametrize(
    "path",
    [
        "/etc/passwd",
        "../outside.py",
        "tests/../secret.py",
        "web_test/coding_agent.py",
        "main.py",
        "pyproject.toml",
        "tests/notes.txt",
        "",
    ],
)
def test_check_write_permission_rejects(path: str) -> None:
    assert not check_write_permission(path).allow


def test_allowed_paths_keeps_only_permitted() -> None:
    paths = ["tests/a.py", "web_test/x.py", "README.md", "pages/p.py", "tests/n.txt"]

    assert allowed_paths(paths) == ["tests/a.py", "pages/p.py"]


def test_resolve_workspace_path_returns_an_existing_python_file(tmp_path: Path) -> None:
    target = tmp_path / "tests" / "test_a.py"
    target.parent.mkdir()
    target.write_text("x = 1\n", encoding="utf-8")

    assert resolve_workspace_path(tmp_path, "tests/test_a.py", suffix=".py") == target


def test_resolve_workspace_path_allows_nested_paths(tmp_path: Path) -> None:
    target = tmp_path / "tests" / "sub" / "test_a.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1\n", encoding="utf-8")

    assert resolve_workspace_path(tmp_path, "tests/sub/test_a.py", suffix=".py") == target


@pytest.mark.parametrize(
    "relative",
    ["/etc/passwd", "../escape.py", "", "tests/../escape.py", "tests/missing.py"],
)
def test_resolve_workspace_path_rejects_unsafe_or_missing(tmp_path: Path, relative: str) -> None:
    assert resolve_workspace_path(tmp_path, relative, suffix=".py") is None


def test_resolve_workspace_path_rejects_the_wrong_suffix(tmp_path: Path) -> None:
    target = tmp_path / "tests" / "notes.txt"
    target.parent.mkdir()
    target.write_text("x = 1\n", encoding="utf-8")

    assert resolve_workspace_path(tmp_path, "tests/notes.txt", suffix=".py") is None


def test_resolve_workspace_path_returns_none_when_resolution_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(self: Path) -> Path:
        raise OSError("cannot resolve")

    monkeypatch.setattr(Path, "resolve", explode)

    assert resolve_workspace_path(tmp_path, "tests/test_a.py", suffix=".py") is None


def test_resolve_workspace_path_rejects_a_symlink_outside(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    outside = tmp_path / "outside.py"
    outside.write_text("x = 1\n", encoding="utf-8")
    link = workspace / "tests" / "link.py"
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)

    assert resolve_workspace_path(workspace, "tests/link.py", suffix=".py") is None


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
