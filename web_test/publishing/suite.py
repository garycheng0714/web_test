from dataclasses import dataclass
from pathlib import Path

from web_test.command import CommandResult, Runner


@dataclass(frozen=True)
class Suite:
    runner: Runner
    workspace: Path

    def run(self) -> CommandResult:
        """Run the suite and keep the deciding output for the caller."""
        return self.runner(
            [
                "uv",
                "run",
                "pytest",
                "-q",
                "--tracing=retain-on-failure",
                "--output=test-results/suite",
            ],
            cwd=self.workspace,
        )
