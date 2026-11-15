# 13: One Phoenix base URL

**What to build:** Delete `export_labels.py`'s private `_base_url` and import the one in `designer_eval/phoenix.py`.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

`designer_eval/phoenix.py:12-27` already owns this: `DEFAULT_ENDPOINT`, `endpoint()` (appends `/v1/traces`, normalising a trailing slash) and `base_url()` (strips it again). `export_labels.py:27` reimplements a third of it, and the two disagree:

- with `PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/`, `base_url()` returns `http://127.0.0.1:6006`, `_base_url()` returns `http://127.0.0.1:6006/`;
- with the suffix present (`.../v1/traces/`), only `endpoint()` handles it.

Both feed a `phoenix.client.Client(base_url=…)`, so the divergence is a double slash in the client's URLs, not an error.

## Tasks

- [x] Import `base_url` from `evals.designer.designer_eval.phoenix` and delete `export_labels._base_url`.
- [x] Keep the `--project` fallback (`args.project or run.project`) unchanged.
- [x] `uv run pytest tests/designer_evals` green.

## Out of scope

- The three probes under `evals/designer/phoenix/`; their fate is ticket 18.
- `run_eval.py:158` and the probes printing `http://127.0.0.1:6006` in a status line.

## Risks

- No test exercises the client: only a live export (`uvx arize-phoenix serve` + `export_labels.py --run …`) proves the normalised URL works against the real server.

## Result

`export_labels.main` now builds the client with `phoenix.base_url()`; `_base_url` and the `os` import are gone. Checked the three endpoint shapes against the shared helper: unset → `http://127.0.0.1:6006`, trailing slash → same without the slash, `/v1/traces` suffix → stripped. A live export is still the only end-to-end proof (see Risks).
