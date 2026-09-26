# 04: PRD parsing module

**What to build:** A module that reads a PRD file and produces the `PRD` model: the base URL
plus a list of requirements with ids.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The module accepts a file path and reads markdown or plain text
- [ ] It produces a `PRD` model (base URL + requirements with unique ids)
- [ ] Requirement ids are assigned when the PRD lacks them
- [ ] Invariants hold: the base URL is valid; every requirement has a non-empty, unique id
- [ ] Error modes are explicit: a missing or unreadable file fails loudly (no silent skip)
- [ ] It is unit-tested at its seam without network access
