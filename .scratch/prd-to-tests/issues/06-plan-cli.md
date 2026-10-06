# 06: CLI — `plan` subcommand

**What to build:** The shared CLI entrypoint with a `plan` subcommand that runs the Test Case
designer on the PRD and writes the test-case document.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `plan --prd <path>` is a required-argument command
- [ ] A missing argument prints usage and exits
- [ ] Running it writes the test-case document at the expected location
- [ ] The CLI entrypoint is shaped so the `automate` subcommand can be added later
