# Go Test Hangs, Deadlocks, And Live Stack Dumps

## Capture A Useful Stack

Use direct `go test`, not a wrapper that filters output. Choose the repository's
artifact directory and module/workspace settings; use GOWORK=off only when intended
module isolation requires it. The temporary path below is illustrative:

```sh
ART="${TMPDIR:-/tmp}/go-test-debug-$(date -u +%Y%m%d_%H%M%S)"
mkdir -p "$ART"
go test ./some/package -run '^TestName$' -count=1 -timeout=30m -v \
  > "$ART/test.log" 2>&1 &
go_pid=$!
```

Find the compiled test binary:

```sh
pgrep -P "$go_pid" -fl '\.test'
```

Verify the exact owned child PID and set `test_pid` to it. SIGQUIT normally dumps
stacks and terminates the test process; it is not a non-destructive snapshot.
Use it only on the authorized diagnostic run. Then send SIGQUIT:

```sh
kill -QUIT "$test_pid"
```

`SIGQUIT` is the reliable Unix signal for a Go goroutine dump. In an interactive terminal, `Ctrl+\` sends it. `Ctrl+C` sends `SIGINT` and usually only interrupts; do not rely on it for stack evidence.

If a Makefile target pipes `go test` through `grep`, the stack dump can be discarded. Stop that run and rerun the package directly with full output.

## What To Count

The active test is the goroutine whose stack includes `testing.tRunner` and the test function. Count:

- which test function is active;
- whether goroutines are blocked on channels, mutexes, IO, external process wait, timers, or `testing.(*T).Parallel`;
- whether the active test is inside production code, test fixture setup, compiler/build setup, or external command execution;
- whether parked goroutines are normal runtime workers, paused parallel tests, or part of the real wait chain.

## Common Stack Meanings

| Stack Pattern | Meaning | Next Step |
|---|---|---|
| `testing.(*T).Parallel` + `chan receive` | Paused parallel test waiting for parent/semaphore, usually not the hang owner. | Find the active non-paused test goroutine. |
| `os/exec.(*Cmd).Run/Wait` + `syscall.Wait4` | Waiting on an external process. | Inspect command, child PID, stdout/stderr, tool cache, and compile/build inputs. |
| `internal/poll.(*FD).Read` under `os/exec` copy goroutine | Reading child process output, often paired with `Cmd.Wait`. | Look at the command being waited on. |
| `sync.runtime_SemacquireMutex` | Mutex wait. | Find owner goroutine or lock ordering. |
| `runtime.chanrecv` / `runtime.chansend` in production code | Channel wait. | Find matching sender/receiver or missing close/cancel. |
| `select` with context/timer channels | Waiting on lifecycle/cancellation. | Verify context cancellation and timeout paths. |
| `time.Sleep` / timers | Deliberate wait. | Check if test uses real time instead of fake clock. |

## Artifact Extraction

Keep the raw log. Also write a filtered summary:

```sh
grep -nE 'SIGQUIT|goroutine [0-9]+ \[|testing\.tRunner|os/exec|sync\.|runtime\.chan|runtime\.select|runtime_Semacquire|Test[A-Za-z0-9_]' \
  "$ART/test.log" > "$ART/stack-summary.txt"
```

For JSON package discovery:

```sh
go test ./some/package -short -shuffle=on -json -timeout=30m \
  > "$ART/package.json.log" 2>&1
```

Use JSON only to identify the last running tests. Use direct `SIGQUIT` output for stack ownership.

## Decision Rules

- If the active stack is in `os/exec` waiting for a compiler/tool, classify it as external tool/runtime duration first, not a Go deadlock.
- If the active stack is in fixture compilation, prefer fixture/cache reuse or isolated package timeout adjustment over production fixes.
- If the active stack is in production code with blocked channel/mutex/select, isolate that exact test and form a hypothesis ledger before patching.
- If all previously exposed tests pass individually and the package times out only as a whole, treat it as cumulative package duration until a stack proves a specific deadlock.
