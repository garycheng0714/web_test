from pathlib import PurePosixPath

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
    if not permission.allow:
        raise ModelRetry(permission.error_msg)
    return args
