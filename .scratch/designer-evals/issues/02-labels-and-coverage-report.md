# 02: Export human labels and report coverage

**What to build:** Read the `HUMAN` annotations from the eval units created by 01, export them
to `labels.jsonl`, and produce a per-run report with coverage rate + Wilson 95% CI, claimed vs
human false tags, and missing/invented/empty/duplicate counts.

`labels.jsonl` is the source of truth for metrics; Phoenix is the annotation UI. A report must
be reproducible from the saved run artifacts, even if Phoenix annotations change later.

**Blocked by:** 01.

**Status:** needs-triage

**Shape:**
- Types: `LabelRecord` (run_id, prd, target_kind, target_id, annotation, label, score,
  annotator, explanation, span_id), `RequirementCoverage` (requirement_id, claimed, covered,
  case_ids), `CoverageReport`.
- Boundary: `units.json` + Phoenix annotations -> `labels.jsonl` -> `report.md` under
  `.scratch/designer-evals/runs/<run_id>/`; eval types are dataclasses, file records are
  Pydantic.
- Invariants: `covered` comes from human `requirement_covered`, not `requirement_ids`; every
  PRD requirement is accounted for; invented IDs are reported, not silently accepted; the
  report includes sample size and CI.

## Tasks

- [ ] Export `requirement_covered` and `case_alignment` annotations by joining `units.json`
      with Phoenix `get_span_annotations`.
- [ ] Include annotator identity in the export and annotation identifier; support one
      annotator now without blocking a second later.
- [ ] Write a reproducible `labels.jsonl` snapshot with run id, PRD, target, label, score,
      explanation, and span id.
- [ ] Compute per-PRD coverage rate + Wilson 95% CI from human labels.
- [ ] Report false tags: claimed by `requirement_ids` but not human-covered.
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
- `requirement_ids` can be gamed; human labels are the ground truth.

## Flow

```text
units.json + Phoenix HUMAN annotations
  │
  ▼
labels.jsonl
  │
  ▼
coverage + Wilson CI + false tags
  │
  ▼
report.md
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`. The coverage/report half of the old
ticket 01.
