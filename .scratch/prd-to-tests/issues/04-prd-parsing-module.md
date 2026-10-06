# 04: PRD parsing module

**What to build:** A module that reads a PRD file and produces the `PRD` model: the base URL
plus a list of requirements with ids.

**Blocked by:** 01

**Status:** wontfix

- [x] The module accepts a file path and reads markdown or plain text
- [x] It produces a `PRD` model (base URL + requirements with unique ids)
- [x] Requirement ids are assigned when the PRD lacks them
- [x] Invariants hold: the base URL is valid; every requirement has a non-empty, unique id
- [x] Error modes are explicit: a missing or unreadable file fails loudly (no silent skip)
- [x] It is unit-tested at its seam without network access

## Comments

Implemented as a structured-output Pydantic AI agent (per the spec's open item, resolved to a
single model call):

- New package `web_test/`:
  - `web_test/prd.py` — `Requirement`, `PRD`, and `parse_prd(path, *, model=None)`. The agent
    runs with `output_type=PRD` and instructions to extract the base URL and requirements and
    assign `R1, R2, …` ids when absent. `path.read_text` raises loudly on a missing/unreadable
    file. `PRD.base_url` is an `HttpUrl`; a `model_validator` fills blank ids and enforces
    non-empty, unique ids.
  - `web_test/model.py` — `resolve_model()` reads `WEB_TEST_MODEL`, default
    `google:gemini-2.5-flash-lite`.
  - `web_test/_run.py` — a loop-agnostic `run_sync(coro)` that runs the coroutine on a fresh
    event loop in a worker thread. Needed because Pydantic AI's `run_sync` fails ("event loop is
    already running") once pytest-playwright's sync tests have started a session loop; this keeps
    the module callable from any context.
- Tests: `tests/test_prd.py` (model overridden with `TestModel(custom_output_args=...)`; id
  assignment; missing-file; duplicate-id and invalid-URL validation) and `tests/test_model.py`
  (env default/override). No network.

`uv run pytest`: 11 passed, 1 failed — only the pre-existing header PUA test the maintainer chose
to leave open.

**Superseded (wontfix).** The first stage became a **single agent** (`PRD text → QaReport`); there
is no standalone PRD parsing module and no `PRD`/`base_url` model. See ADR-0005. The implemented
`web_test/prd.py` and `tests/test_prd.py` were removed. Requirement traceability now rides on each
test case as `requirement_ids` (ticket 05).
