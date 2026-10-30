from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict
from pydantic_ai import ModelRetry, RunContext, ToolDefinition
from pydantic_ai.capabilities import ValidatedToolArgs
from pydantic_ai.capabilities.hooks import Hooks
from pydantic_ai.messages import ToolCallPart

ALLOWED_DIRS = ("tests", "pages", "components")


class WritePermission(BaseModel):
    model_config = ConfigDict(frozen=True)

    error_msg: str | None = None

    @property
    def allow(self) -> bool:
        return self.error_msg is None


def check_write_permission(path: str) -> WritePermission:
    """Whether a write to `path` is allowed, with a reason when it is not."""
    return WritePermission(error_msg=_rejection_reason(path))


def allowed_paths(paths: list[str]) -> list[str]:
    """The subset of `paths` the write guard permits."""
    return [path for path in paths if check_write_permission(path).allow]


def is_generated_test_path(relative: str) -> bool:
    """Whether a changed path is a generated test file under `tests/`."""
    candidate = PurePosixPath(relative)
    return candidate.suffix == ".py" and candidate.parts[:1] == ("tests",)


def resolve_workspace_path(workspace: Path, relative: str, *, suffix: str) -> Path | None:
    """Resolve a relative path to an existing file inside the workspace, or None."""
    candidate = PurePosixPath(relative)
    if (
        candidate.is_absolute()  # 拒絕絕對路徑（如 /etc/passwd）
        or not candidate.parts  # 空路徑（""）
        or ".." in candidate.parts  # 拒絕目錄穿越（../）
        or candidate.suffix != suffix  # 只收指定副檔名
    ):
        return None
    path = workspace / Path(*candidate.parts)
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if not resolved.is_relative_to(workspace.resolve()) or not resolved.is_file():
        return None
    return path


def _rejection_reason(path: str) -> str | None:
    candidate = PurePosixPath(path)
    if candidate.is_absolute():
        return f"{path!r} is absolute; write a path under one of {ALLOWED_DIRS}."
    if ".." in candidate.parts:
        return f"{path!r} escapes the workspace."
    if candidate.suffix != ".py":
        return f"{path!r} is not a Python file."
    if not candidate.parts or candidate.parts[0] not in ALLOWED_DIRS:
        return f"{path!r} is outside {ALLOWED_DIRS}."
    return None


write_guard = Hooks(id="write_guard")


@write_guard.on.before_tool_execute(tools=["write_file", "edit_file"])
async def _guard(
    ctx: RunContext[None],
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: ValidatedToolArgs,
) -> ValidatedToolArgs:
    permission = check_write_permission(args["path"])
    if permission.error_msg is not None:
        raise ModelRetry(permission.error_msg)
    return args
