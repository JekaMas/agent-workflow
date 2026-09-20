---
name: golang-testing
description: Diagnose Go test hangs, timeouts, deadlocks or unusual slowness using isolated tests and goroutine stacks.
metadata:
  short-description: Debug Go test hangs and timeouts
---

# Go Testing

Use this skill for Go test failures where the problem is not an ordinary assertion: hangs, package timeouts, slow tests, suspected deadlocks, blocked goroutines, or unknown long-running tests.

## First Rule

Do not treat a package timeout as a semantic failure. Identify the active test and capture live stacks before fixing code.

## Workflow

1. Run the narrowest known failing package or test directly, with full output redirected to an artifact file.
2. Avoid wrappers that filter output, such as `grep`-filtered Makefile targets, when collecting stack evidence.
3. If the run appears stuck, send `SIGQUIT` to the compiled `*.test` process, not the shell wrapper.
4. Parse the goroutine dump and classify the wait owner.
5. Rerun only the identified test in isolation before rerunning a broad suite.

For the exact SIGQUIT workflow and stack interpretation, read `references/live-deadlocks.md`.
