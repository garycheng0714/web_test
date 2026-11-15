# 16: Type the Phoenix annotation rows `export_labels` reads

**What to build:** Give the Phoenix API response a model, so `export_labels.py` stops reading `Sequence[Any]` by string key.

**Blocked by:** Nothing. Ticket 13 touches the same file but not the same lines.

**Status:** ready-for-agent

## Why

Every other boundary in the eval package now has a model (`AnnotationRow`, `LabeledClaim`, `RunSummary`, `EvalUnit`, `DesignOutput`). The one left is the input side of `export_labels.py`:

- `_alignment_by_span(annotations: Sequence[Any])` at line 39 reads `annotation["span_id"]`, `annotation["annotator_kind"]`, `annotation["name"]`, `annotation.get("result")`;
- `_label_rows(units, annotations: Sequence[Any], run, …)` at line 47 does the same for `id`, `identifier`, `source`, `metadata`.

A renamed field upstream is a `KeyError` inside a list comprehension today, or a silent `None` via `.get("result")`. The tests fabricate these dicts by hand, so they would not notice a drift between the fixture and the real API.

## Shape

- Types: `PhoenixAnnotation` model in `designer_eval/labels.py` (it is the exported annotation, the same vocabulary as `AnnotationRow`): `id: str | None`, `span_id: str`, `name: str`, `annotator_kind: Literal["HUMAN", "CODE"]`, `result: AnnotationResult | None`, `identifier: str = ""`, `source: str | None = None`, `metadata: dict[str, object] = {}`; and `AnnotationResult` with `label: str | None`, `score: float | None`, `explanation: str | None`.
- Boundary: the `phoenix.client` span-annotation response, in memory only (never a file).
- Invariants: a row without `span_id` or `annotator_kind` fails to validate; a missing `result` stays allowed, because the current code tolerates it with `or {}`.

## Tasks

- [ ] Capture one real response shape first: run `uvx arize-phoenix serve`, export one run, and record which keys the client actually returns (the tests' dicts are the only evidence today, and they were typed by hand).
- [ ] Add the two models; validate the response in `export_labels.main()` before it reaches `_label_rows`.
- [ ] Type `_alignment_by_span` and `_label_rows` against them; keep the "failure mode on a passing claim is dropped" rule where it is.
- [ ] Move the test fixtures to the model, and keep one test that proves a row without `annotator_kind` fails.
- [ ] `uv run pytest tests/designer_evals` green; `uv run --group eval basedpyright` clean.

## Out of scope

- Typing the rest of the Phoenix client (`client.spans.get_span_annotations`, `Client` construction).
- `AnnotationRow` itself; it is the output shape and already typed.

## Risks

- The live client may return `result: null` versus omitting `result`, and may include fields the fixtures do not have. Model the response as optional-tolerant; do not tighten a field the API omits.
- Phoenix version drift is the reason this ticket exists, but a strict model turns a harmless new field into a failed export only if `extra="forbid"` is set. Keep the default (`ignore`).
