# 02: Export human labels and report coverage

**What to build:** Read the `HUMAN` annotations from the eval units created by 01, export them
to `labels.jsonl`, and produce a per-run report with coverage rate + Wilson 95% CI, claimed vs
human false tags, and missing/invented/empty/duplicate counts.

`labels.jsonl` is the source of truth for metrics; Phoenix is the annotation UI. A report must
be reproducible from the saved run artifacts, even if Phoenix annotations change later.

**Blocked by:** 01.

**Status:** needs-triage

**Shape:**
- Types: `LabelRecord` (run_id, prd, target_kind `claim`/`requirement`, target_id,
  annotation, label, score, annotator, explanation, span_id), `RequirementCoverage`
  (requirement_id, claimed, covered, claim_ids, case_ids), `CoverageReport`.
- Boundary: `units.json` + Phoenix annotations -> `labels.jsonl` -> `report.md` under
  `.scratch/designer-evals/runs/<run_id>/`; eval types are dataclasses, file records are
  Pydantic.
- Invariants: a requirement is `covered` when at least one human `claim_alignment` on its
  claims is `pass`; all claims failing means `not_covered`; no claim means `missing`. Missing
  requirement spans may carry `requirement_covered` as confirmation, but they do not replace
  claim labels. Invented IDs are reported, not silently accepted; the report includes sample
  size and CI.

## Tasks

- [ ] Export `claim_alignment` and `requirement_covered` annotations by joining `units.json`
      with Phoenix `get_span_annotations`.
- [ ] Include annotator identity in the export and annotation identifier; support one
      annotator now without blocking a second later.
- [ ] Write a reproducible `labels.jsonl` snapshot with run id, PRD, target, label, score,
      explanation, and span id.
- [ ] Compute per-PRD coverage rate + Wilson 95% CI from claim labels.
- [ ] Report false tags: claimed by `requirement_ids` but no claim passes.
- [ ] Report missing requirements, invented IDs, empty IDs, and duplicate cases.
- [ ] Reuse `web_test/planning/review/structure.py` for structural checks.
- [ ] Add tests for Wilson CI and the labels/units join.
- [ ] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
      `uv run ruff check --select F401`.

## Out of scope

- Semantic judge (ticket 03).
- Phoenix experiments (ticket 04).
- CI or gate changes.
- Changing the designer prompt/model.

## Risks

- Small PRD sample; CIs will be wide.
- Single annotator; use delayed self-review or add a second person.
- Phoenix annotations and `labels.jsonl` can drift; export snapshots are mandatory.
- `requirement_ids` can be gamed; human claim labels are the ground truth.
- A case claiming multiple requirements produces multiple claim labels; join by claim id.

## Flow

```text
units.json + Phoenix HUMAN claim labels
  │
  ▼
labels.jsonl
  │
  ▼
coverage derived from claims + Wilson CI + false tags
  │
  ▼
report.md
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`. The coverage/report half of the old
ticket 01.
