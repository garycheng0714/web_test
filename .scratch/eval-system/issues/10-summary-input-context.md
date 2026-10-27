# 10: Show the input and open questions in the verification summary

**What to build:** The verification summary names the PRD path and, when the artifact carries open
questions, lists them, so a reviewer does not have to hunt for the input or the unresolved
behaviour.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The summary names the PRD path
- [ ] Open questions from the artifact are listed, or "none" is stated
- [ ] The full PRD is not dumped into the summary
- [ ] The markdown renders correctly on GitHub
- [ ] Tests cover the rendering with and without open questions

## Decisions / assumptions

- A path is enough for a reviewer with the repository; the full text is not copied.
- The artifact's `## Open Questions` section is the source when present.
- This is a display change; it does not change the verdict.

## Out of scope

- Showing the designer's full reasoning or trace.
- Links to GitHub URLs (a path is portable across the API and the check summary).
