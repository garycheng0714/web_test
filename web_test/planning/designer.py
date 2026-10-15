from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Skills

from web_test._run import run_sync
from web_test.model import resolve_design_model
from web_test.paths import REPO_ROOT
from web_test.planning.schema import DesignOutput

# `Skills` takes a *library* directory, not a single skill: it scans the immediate child
# directories and turns each one that has a `SKILL.md` into a deferred capability. This
# library contains exactly one skill; `include` keeps the catalog to it explicitly, and
# `workspace` is where the library is read from (required — a run with no workspace fails).
SKILL_LIBRARY = REPO_ROOT / ".agents" / "libraries" / "test_case_designer"
SKILL_NAME = "qa-test-case-generation"

INSTRUCTIONS = (
    "You design QA test cases from a PRD. First call load_capability("
    f"'{SKILL_NAME}') to load the qa-test-case-generation skill, then follow it to produce "
    "the test cases and the open questions as the structured result."
)


def design_test_cases(prd_text: str, *, model: Model | str | None = None) -> DesignOutput:
    agent = Agent(
        model or resolve_design_model(),
        name="test_case_designer",
        output_type=DesignOutput,
        instructions=INSTRUCTIONS,
        capabilities=[
            Skills(
                str(SKILL_LIBRARY),
                include=[SKILL_NAME],
                workspace=LocalWorkspaceBackend(str(REPO_ROOT)),
            )
        ],
    )
    return run_sync(agent.run(prd_text)).output
