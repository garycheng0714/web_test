# 25: Close repeated findings at the root

**What to build:** A mapping from each repeated finding class to the mechanism that prevents it: a
deterministic check, a designer skill rule, or a regression fixture. When a finding class can be
checked without judgment, it moves to code; when it cannot, the designer skill gains one rule and a
variant proves the rule is needed. No rule is added twice as prose.

**Blocked by:** 22 (22b parked).

**Status:** needs-triage

- [ ] A table lists each finding class and its enforcement mechanism
- [ ] Each class has a variant in the eval set
- [ ] Classes that can be decided mechanically have a deterministic check
- [ ] Remaining classes have one skill rule each, not a growing prose list
- [ ] The eval run stays green after the changes

## Comments

**2026-10-24 — metadata.** 20 is done; only 22 remains, and its coverage slice (22b) is parked.
