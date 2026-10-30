## Verification

**Status:** `FAIL`

## Jev review

**Jev status:** `FAIL`

**AC alignment:** 2/3 cases aligned

**Step quality:** 3/3 reasonable, 2/3 continuity, 3/3 observable

**Findings**

- Case 2: B (AC alignment, p=0.05)

**Needs review**

- Case 3, step 1: Go (continuity, p=0.6)

**Blocked**

None.

**Evidence**

- PRD: `sha256:0063ca4546ac82e2b33f97ae38ee5197a9bfda52149f10129c1cf735e71d63d2`
- Test Case: `sha256:c7c5c1d70c5dec4416ab6158afd0b223ef40c29b1dc1f97ed9428b94d4cadb1c`
- Model: `jev-1.13.0`
- Question set: `870beda23e21eb27`
- Check set: `structure-v1`
- Bands: pass >= 0.8, needs review >= 0.5

_Required-check contract: PASS or an adjudicated NEEDS_REVIEW/BLOCKED; FAIL is not overridable._