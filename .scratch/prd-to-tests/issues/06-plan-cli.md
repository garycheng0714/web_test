# 06: CLI — `plan` subcommand

**What to build:** The shared CLI entrypoint with a `plan` subcommand that invokes PRD parsing
and the Test Case designer and writes the test-case document.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `plan --prd <path>` is a required-argument command
- [ ] A missing argument prints usage and exits
- [ ] A command-line base-URL override is accepted and takes precedence over the PRD value
- [ ] Running it writes the test-case document at the expected location
- [ ] The CLI entrypoint is shaped so the `automate` subcommand can be added later
