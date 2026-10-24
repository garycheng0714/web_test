# 04: Agent-produced PR body

**What to build:** After the generated tests pass, the same coding agent writes the PR body following the
repo's `pr` skill (Summary / Evidence / Merge Danger), and the automation stage returns that body for the
publisher to use. A red suite produces no body.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; implemented)

- [x] The coding agent can load the `pr` skill on demand
- [x] On green, the agent's output is a PR body following the skill's template
- [x] On red, the agent stops and produces no PR body
- [x] An agent-level test (model overridden) asserts red produces no body and green produces one

## Comments

Approach: the green/red gate lives in the agent (a single run), and the automation stage returns a
structured result.

- `web_test/automation/coding_agent.py` — the agent's `Skills` now reads **two** libraries,
  `.agents/libraries/coding_agent` (the house `page-object-model`) and `.agents/skills` (for `pr`),
  with `include=["page-object-model", "pr"]`, so the model can `load_capability('pr')` on demand.
  Added `AutomationResult(BaseModel)` with `pr_body: str | None = None` (boundary/model output per
  the house convention) and set `output_type=AutomationResult`; `create_automation` now returns it.
  `INSTRUCTIONS` gained the rule: once green, `load_capability('pr')` and write the body in its
  template as `pr_body`; if still red after 3 attempts, return `pr_body` as null.
- `tests/automation/test_coding_agent.py` — the ticket-03 through-agent test now ends with the
  `final_result` output call (structured output). Two new model-overridden tests:
  `test_green_run_produces_a_pr_body` scripts `load_capability('pr')` then `final_result` with a
  body, and asserts the `load_capability` tool return carries `# Skill: pr` (item 1) and
  `result.output.pr_body` is the body (item 2); `test_red_run_produces_no_pr_body` scripts
  `final_result` with `pr_body=None` and asserts `result.output.pr_body is None` (item 3).

Why the gate is agent-side: the ticket asks for the *same coding agent* to write the body and to be
tested with the model overridden; and the deterministic backstop already exists in the publisher
(`publish()` re-runs the suite and opens no PR on red). The cost, noted honestly: this makes the
red/green test a contract test — it exercises the output plumbing and shape, while the policy itself
lives in `INSTRUCTIONS`. The test does prove the `pr` skill is loadable at run time.

`uv run pytest`: 52 passed, 1 skipped (the pre-existing Products PUA header test).

Left for ticket 05: wire `create_automation`'s `AutomationResult` into the publisher's `body`.

**2026-10-24 — bookkeeping: done.**

`AutomationResult.pr_body` is wired into the publisher body and covered by `tests/automation`. Status → `ready-for-human (done; implemented)`.
