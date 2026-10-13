from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.models import Model
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Coder, Skills
from pydantic_ai_harness.playwright import EgressPolicy, PlaywrightBrowser

from web_test._run import run_sync
from web_test.model import resolve_model
from web_test.paths import REPO_ROOT
from web_test.write_guard import write_guard

# `Skills` takes a *library* directory (its immediate child directories with a `SKILL.md`), not a
# single skill. Two libraries are read: the page-object-model house skill, and the repo's `.agents/skills`
# for the `pr` skill. Both are read from the repo, not the run workspace, so the agent can work in a
# throwaway clone and still load the house conventions.
SKILL_LIBRARY = REPO_ROOT / ".agents" / "libraries" / "coding_agent"
PR_SKILL_LIBRARY = REPO_ROOT / ".agents" / "skills"
SKILL_NAME = "page-object-model"
PR_SKILL_NAME = "pr"


class AutomationResult(BaseModel):
    """What an automation run returns: the PR body, or nothing when the suite stayed red."""

    pr_body: str | None = None


GROUNDING_DOMAINS = ["automationexercise.com"]

# Ad networks observed injecting an interstitial that covers the SUT's header and swallows clicks
# (see .scratch/known-issues.md). `allowed_domains` leaves passive subresources alone, so only a
# blocked_domains entry stops the ad script and its frame; the same list as tests/conftest.py.
AD_DOMAINS = [
    "googlesyndication.com",
    "doubleclick.net",
    "googleadservices.com",
    "googletagservices.com",
    "adtrafficquality.google",
]

GROUNDING_POLICY = EgressPolicy(allowed_domains=GROUNDING_DOMAINS, blocked_domains=AD_DOMAINS)

INSTRUCTIONS = (
    "You implement Playwright Python automation tests from QA test cases. Before writing any "
    f"test, call load_capability('{SKILL_NAME}') to load the {SKILL_NAME} skill, then follow it "
    "and the repository's existing conventions.\n\n"
    "Grounding: before writing locators, identify the pages the case traverses. Reuse page "
    "objects/components already in `pages/` and `components/`; for a page not yet encapsulated, "
    "ground it live with the browser tools: `navigate(<url>)` to open it, then `snapshot()` to "
    "read the accessibility tree and target elements by the `aria-ref` handles it returns. The "
    "browser starts on first use and closes when the run ends, so there is no close step. Take "
    "the base URL from the case's front-matter `base_url`. If it cannot be determined, stop and "
    "report what is missing rather than guessing.\n\n"
    "Verify: after writing, run `uv run pytest <path> -q`. If it fails, fix it and rerun, up to 3 "
    "attempts. Only claim success when the run is green. When it is green, call "
    f"load_capability('{PR_SKILL_NAME}') and write the pull-request body for these changes in that "
    "skill's template, returning it as `pr_body`. When the suite is still red after 3 attempts, "
    "stop and return `pr_body` as null — never write a body for a red suite. Keep comments "
    "minimal, matching the surrounding code."
)


def build_automation_agent(
    model: Model | str, *, workspace_dir: str | Path
) -> Agent[object, AutomationResult]:
    """Assemble the coding agent that grounds and writes tests inside `workspace_dir`.

    Kept separate from `create_automation` so a test can inspect the agent's capabilities and
    tools without running it.
    """
    return Agent(
        model,
        name="automation_coding_agent",
        output_type=AutomationResult,
        instructions=INSTRUCTIONS,
        capabilities=[
            LocalWorkspace(str(workspace_dir)),
            Coder(sub_agents=False, repo_context=False),
            write_guard,
            Skills(
                [str(SKILL_LIBRARY), str(PR_SKILL_LIBRARY)],
                include=[SKILL_NAME, PR_SKILL_NAME],
                workspace=LocalWorkspaceBackend(str(REPO_ROOT)),
            ),
            PlaywrightBrowser(policy=GROUNDING_POLICY),
        ],
    )


def create_automation(
    test_steps: str,
    model: Model | str | None = None,
    *,
    workspace_dir: str | Path,
) -> AutomationResult:
    """Turn QA test steps into Playwright Python tests inside `workspace_dir`.

    `workspace_dir` is the repository the agent reads and edits (e.g. a throwaway clone).
    A run without a workspace fails at its start, so it is required.
    """
    agent = build_automation_agent(model or resolve_model(), workspace_dir=workspace_dir)
    return run_sync(agent.run(test_steps)).output
