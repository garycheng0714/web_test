import json
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from web_test.command import Runner


@dataclass(frozen=True)
class PullRequest:
    """The pull request to open, passed between `publish` and `GitHub`."""

    base: str
    head: str
    title: str
    body: str


class CheckConclusion(StrEnum):
    """The conclusion the verification check reports to GitHub."""

    SUCCESS = "success"
    ACTION_REQUIRED = "action_required"
    FAILURE = "failure"


class CheckPayload(BaseModel):
    """The check run to publish for one head SHA."""

    name: str = "verify-test-case"
    head_sha: str
    conclusion: CheckConclusion
    title: str
    summary: str
    external_id: str
    status: Literal["completed"] = "completed"


@dataclass(frozen=True)
class GitHub:
    run: Runner
    workspace: Path

    def open_pull_request(self, pr: PullRequest) -> None:
        self.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                pr.base,
                "--head",
                pr.head,
                "--title",
                pr.title,
                "--body",
                pr.body,
            ],
            cwd=self.workspace,
        ).check()

    def find_check_run(self, head_sha: str, *, repo: str, name: str) -> int | None:
        """The existing check run id for `name` on `head_sha`, or `None`."""
        result = self.run(
            ["gh", "api", f"repos/{repo}/commits/{head_sha}/check-runs?check_name={name}"],
            cwd=self.workspace,
        ).check()
        runs = json.loads(result.stdout).get("check_runs", [])
        return int(runs[0]["id"]) if runs else None

    def publish_check(self, payload: CheckPayload, *, repo: str) -> None:
        """Create the check run, or update the one already on the head SHA."""
        run_id = self.find_check_run(payload.head_sha, repo=repo, name=payload.name)
        body = {
            "name": payload.name,
            "head_sha": payload.head_sha,
            "status": payload.status,
            "conclusion": payload.conclusion.value,
            "output": {"title": payload.title, "summary": payload.summary},
            "external_id": payload.external_id,
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(body, handle)
            path = Path(handle.name)
        try:
            endpoint = f"repos/{repo}/check-runs" + (f"/{run_id}" if run_id else "")
            method = "PATCH" if run_id else "POST"
            self.run(
                ["gh", "api", "--method", method, endpoint, "--input", str(path)],
                cwd=self.workspace,
            ).check()
        finally:
            path.unlink(missing_ok=True)
