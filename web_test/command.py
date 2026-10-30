import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""

    def check(self) -> "CommandResult":
        """Raise when the command failed."""
        if self.returncode != 0:
            raise RuntimeError(self.stderr.strip() or f"command failed (exit {self.returncode})")
        return self


Runner = Callable[..., CommandResult]


def subprocess_runner(args: list[str], *, cwd: str | Path | None = None) -> CommandResult:
    proc = subprocess.run(  # noqa: S603 - argv list with shell=False: no shell to inject into
        args, cwd=cwd, capture_output=True, text=True, check=False
    )
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)
