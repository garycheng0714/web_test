# 16: Type the Phoenix annotation rows `export_labels` reads

**What to build:** Give the Phoenix API response a model, so `export_labels.py` stops reading `Sequence[Any]` by string key.

**Blocked by:** Nothing. Ticket 13 touches the same file but not the same lines.

**Status:** ready-for-review

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

- [x] Capture the response shape. No local Phoenix holds these runs' spans any more, so the source was the installed client's own types (`phoenix.client.resources.spans.SpanAnnotation` and `v1.AnnotationResult`, arize-phoenix-client 3.5.0); a live export is still the end-to-end check.
- [x] Add the two models; validate the response in `export_labels.main()` before it reaches `_label_rows`.
- [x] Type `_alignment_by_span` and `_label_rows` against them; keep the "failure mode on a passing claim is dropped" rule where it is.
- [x] Move the test fixtures to the model, and keep one test that proves a row without `annotator_kind` fails.
- [x] `uv run pytest tests/designer_evals` green; `uv run --group eval basedpyright` clean.

## Out of scope

- Typing the rest of the Phoenix client (`client.spans.get_span_annotations`, `Client` construction).
- `AnnotationRow` itself; it is the output shape and already typed.

## Risks

- The live client may return `result: null` versus omitting `result`, and may include fields the fixtures do not have. Model the response as optional-tolerant; do not tighten a field the API omits.
- Phoenix version drift is the reason this ticket exists, but a strict model turns a harmless new field into a failed export only if `extra="forbid"` is set. Keep the default (`ignore`).

## Result

`designer_eval/labels.py` now has `PhoenixAnnotation` and `AnnotationResult`. `export_labels.main`
validates the client's response into them before `_label_rows` sees it, and both helpers take the
model instead of `Sequence[Any]`.

Reading the client's declared types paid for itself: `annotator_kind` is `Literal["HUMAN", "CODE",
"LLM"]`, and an LLM annotation would have crashed `AnnotationRow` (which accepted two kinds) and
been written with `annotator: "code"`. `AnnotationRow.annotator_kind` now accepts the three values
and a non-HUMAN row records `kind.lower()`. No committed label row changes: all 251 rows across the
six runs still read and rewrite byte-identically.

Tests: a fixture without `annotator_kind` fails, and an LLM annotation fails. 391 passed,
basedpyright clean, 7 contracts kept.

Still unverified: no live Phoenix export was run (the local instance does not hold these spans), so
the payload is checked against the client's types, not against a real response.

## Comments

2026-11-15: the human chose the strict form. `PhoenixAnnotation` is narrowed to the two kinds we
keep rather than describing everything the client can return, and a rejected LLM row surfaces as a
pydantic traceback on purpose — the alternative (accept three, drop LLM with an `ignored N` count)
was rejected as silently skipping data. The cost is accepted knowingly: enabling an LLM evaluator on
the `web-test-designer-eval` project makes every export fail until the type is widened again.
