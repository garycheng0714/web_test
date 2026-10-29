# 02: Export human labels and report coverage

**What to build:** Read the `HUMAN` annotations from the eval units created by 01, export them
to `labels.jsonl`, and produce a per-run report with coverage rate + Wilson 95% CI, claimed vs
human false tags, and missing/invented/empty/duplicate counts.

`labels.jsonl` is the source of truth for metrics; Phoenix is the annotation UI. A report must
be reproducible from the saved run artifacts, even if Phoenix annotations change later.

**Blocked by:** 01.

**Status:** ready-for-human

**Shape:**
- Types: `LabelRecord` (run_id, prd, target_kind `claim`/`requirement`, target_id,
  annotation, annotator_kind, label, score, annotator, explanation, span_id, annotation_id,
  source, metadata), `RequirementCoverage` (requirement_id, claimed, covered, status,
  claim_ids, case_ids), `CoverageReport`.
- Boundary: `units.json` + Phoenix annotations -> `labels.jsonl` -> `report.md` under
  `.scratch/designer-evals/runs/<run_id>/`; eval types are dataclasses, file records are
  Pydantic.
- Invariants: a requirement is `covered` when at least one human `claim_alignment` on its
  claims is `pass`; all claims failing means `not_covered`; no claim means `missing`. Missing
  requirement spans may carry `requirement_covered` as confirmation, but they do not replace
  claim labels. Invented IDs are reported, not silently accepted; the report includes sample
  size and CI.

## Tasks

- [x] Export `claim_alignment`, `requirement_covered`, and CODE annotations by joining
      `units.json` with Phoenix `get_span_annotations`.
- [x] Record HUMAN annotations as `local`; keep `annotator_kind` and `annotation_id` in the
      snapshot.
- [x] Write a reproducible `labels.jsonl` snapshot with run id, PRD, target, label, score,
      explanation, and span id.
- [x] Compute per-PRD coverage rate + Wilson 95% CI from claim labels.
- [x] Report false tags: claimed by `requirement_ids` but no claim passes.
- [x] Report missing requirements, invented IDs, empty IDs, and duplicate cases.
- [x] Reuse `web_test/planning/review/structure.py` for structural checks.
- [x] Add tests for Wilson CI, label export, coverage, false tags, and a synthetic fake fail.
- [x] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
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

2026-10-29: `export_labels.py` and `report.py` implemented. Run
`register-login-20261029T070829Z` exported 7 HUMAN + 14 CODE labels; report shows 6/6
requirements covered, Wilson 95% CI [0.61, 1.00], no false tags or code failures.
The test suite includes a synthetic fake-fail claim to exercise the false-tag path.
