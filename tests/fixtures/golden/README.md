# Golden outputs

Whole-file snapshots of the text this repo shows to a human: the verification report that becomes
part of the PR body, and the rendered Test Case document.

## Files

| File | Rendered by |
| --- | --- |
| `review_report_fail.md` | `render_report` on a FAIL record with findings and needs-review items |
| `review_report_blocked.md` | `render_report` on a BLOCKED record |
| `case_document_register_login.md` | `render_document` for one case with an escaped pipe, a line break, preconditions, notes, and an open question |

The tests that compare them live in `tests/planning/test_golden_outputs.py`.

## Updating

There is no update flag on purpose. When a change to the text is intended:

1. Run `uv run pytest tests/planning/test_golden_outputs.py -q`.
2. Read the unified diff in the failure message.
3. Write the new text into the golden file by hand.
4. Re-run the test and commit the golden with the change that caused it.

The diff is the review. Copying a whole file without reading it defeats the test.
