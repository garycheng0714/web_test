import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


Runner = Callable[..., CommandResult]


def subprocess_runner(args: list[str], *, cwd: str | Path | None = None) -> CommandResult:
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def run_checked(run: Runner, args: list[str], *, cwd: str | Path | None = None) -> None:
    """Run a command and raise when it fails."""
    result = run(args, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr.strip()}")
