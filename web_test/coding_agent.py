from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.models import Model
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Coder, Skills

from web_test._run import run_sync
from web_test.model import resolve_model
from web_test.paths import REPO_ROOT
from web_test.write_guard import write_guard

# `Skills` takes a *library* directory (its immediate child directories with a `SKILL.md`), not a
# single skill. This library holds the page-object-model skill; `include` keeps the catalog to it.
# The library is read from the repo, not the run workspace, so the agent can work in a throwaway
# clone and still load the house conventions.
SKILL_LIBRARY = REPO_ROOT / ".agents" / "libraries" / "coding_agent"
SKILL_NAME = "page-object-model"

INSTRUCTIONS = (
    "You implement Playwright Python automation tests from QA test cases. Before writing any "
    f"test, call load_capability('{SKILL_NAME}') to load the {SKILL_NAME} skill, then follow it "
    "and the repository's existing conventions.\n\n"
    "Grounding: before writing locators, identify the pages the case traverses. Reuse page "
    "objects/components already in `pages/` and `components/`; for a page not yet encapsulated, "
    "ground it live with `playwright-cli` (`open <url>`, `--raw snapshot`, then `close`). Take "
    "the entry URL from the case text, or from `DEFAULT_BASE_URL` in `pages/base_page.py` when "
    "the case gives none. If a page's URL cannot be determined, stop and report what is missing "
    "rather than guessing.\n\n"
    "Verify: after writing, run `uv run pytest <path> -q`. If it fails, fix it and rerun, up to 3 "
    "attempts. Only claim success when the run is green, and report the actual pytest output. "
    "Keep comments minimal, matching the surrounding code."
)


def create_automation(
    test_steps: str,
    model: Model | str | None = None,
    *,
    workspace_dir: str | Path,
) -> str:
    """Turn QA test steps into Playwright Python tests inside `workspace_dir`.

    `workspace_dir` is the repository the agent reads and edits (e.g. a throwaway clone).
    A run without a workspace fails at its start, so it is required.
    """
    agent = Agent(
        model or resolve_model(),
        name="automation_coding_agent",
        instructions=INSTRUCTIONS,
        capabilities=[
            LocalWorkspace(str(workspace_dir)),
            Coder(),
            write_guard,
            Skills(
                str(SKILL_LIBRARY),
                include=[SKILL_NAME],
                workspace=LocalWorkspaceBackend(str(REPO_ROOT)),
            ),
        ],
    )
    return run_sync(agent.run(test_steps)).output
