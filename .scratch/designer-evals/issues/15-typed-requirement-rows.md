# 15: Type the report's requirement rows

**What to build:** Replace `requirement_rows`' `list[dict]` with a dataclass, and stop passing eight keyword arguments into the two builders.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

`report.py:39-97` (`requirement_rows`) builds rows as dicts whose values are `str`, `list[str]`, `bool`, `int` and `list[AnnotationRow]` mixed together. Three renderers then index them by string key (`row["claim_ids"]`, `row["status"]`, `row["labels"]`, …). Nothing checks that a key exists, and `_code_check_lines` / `_coverage_lines` each take eight keyword arguments assembled by hand in `render_report`.

Since the boundary files were typed, this is now the only untyped shape inside the report path.

## Shape

- Types: `@dataclass(frozen=True) class RequirementRow` — internal data between our own modules, so a dataclass, not a model: `requirement_id: str`, `claim_ids: list[str]`, `case_ids: list[str]`, `missing: bool`, `status: str`, `labels: list[AnnotationRow]`, `pass_count: int`, `tested: bool`.
- Boundary: none; nothing here is read from or written to disk.
- Invariants: the rendered text does not change; a requirement with no claim cannot be `covered`.

## Tasks

- [ ] Add `RequirementRow` and return it from `requirement_rows`.
- [ ] Make the renderers take the row instead of a dict.
- [ ] Fold `_code_check_lines`' and `_coverage_lines`' argument lists into one value the caller already has, or compute inside them.
- [ ] Verify the report text is unchanged: render `realworld-v06-20261113` and `journey-v07-20261103` with the previous and the new code and diff.
- [ ] `uv run pytest tests/designer_evals` green.

## Out of scope

- Any change to the report's sections, wording or ordering.
- `render_report`'s signature (already typed in the previous refactor).

## Risks

- `labels` inside a row are already used for two different purposes (`_requirement_lines` renders `label(annotator)`, `_not_clean_lines` renders `target_id=label`); a different order of the list changes the text.
