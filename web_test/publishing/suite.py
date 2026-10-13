from dataclasses import dataclass
from pathlib import Path

from web_test.command import Runner


@dataclass(frozen=True)
class Suite:
    run: Runner
    workspace: Path

    def is_green(self) -> bool:
        return self.run(["uv", "run", "pytest", "-q"], cwd=self.workspace).returncode == 0
