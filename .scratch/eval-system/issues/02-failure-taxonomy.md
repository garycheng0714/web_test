# 02: Build an observed failure taxonomy

**What to build:** A named taxonomy of the ways the designer and the automation agent actually
fail, grounded in observed outputs rather than brainstormed labels. Each mode names the stage,
gives one real example, and names the check that would catch it. The result feeds the datasets
in 04, 07, and 08.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [ ] At least 20 outputs reviewed across both stages (existing logs count; add runs if needed)
- [ ] Every mode is observed in at least one output, with the example quoted or linked
- [ ] Each mode names the stage, the trigger, and the check that would catch it
- [ ] Generic labels ("hallucination", "quality") are rejected in favour of application-specific ones
- [ ] The taxonomy is a file in this feature directory and lists candidate cases for the datasets
- [ ] No interactive review app is required; a batch review is enough

## Decisions / assumptions

- "Observed" means it appears in a saved output, run log, trace, or evidence artifact.
- The existing `.scratch/agent-in-ci` observations are inputs, not the finished taxonomy.
- A mode that no check can catch is still recorded; it becomes a candidate for a new check.

## Out of scope

- Labeling every case.
- Metrics or reports.
- A review UI.
