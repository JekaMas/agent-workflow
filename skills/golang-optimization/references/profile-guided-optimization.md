# Profile-Guided Optimization

Use PGO after source-level optimization and only for a final Go executable.
PGO changes compiler decisions for the whole program, including dependencies;
it is not a library-local build flag or a substitute for profiles and source
diagnostics.

Primary references:

- [Go profile-guided optimization](https://go.dev/doc/pgo)
- [Cloudflare: Reclaiming CPU for free with PGO](https://blog.cloudflare.com/reclaiming-cpu-for-free-with-pgo/)

## Ownership Gate

The profile belongs to the deployed `main` package and its workload.

- Prefer CPU profiles captured from representative production instances.
- If production profiles are unavailable, use a mixed application benchmark or
  replay and label the result experimental. A single microbenchmark is usually
  not representative enough to authorize PGO.
- Do not commit `default.pgo` to a library and claim downstream improvement.
  The consuming executable must collect, own, validate, and select its profile.
- Keep profile collection free of secrets and high-cardinality request data.
- Refresh profiles after material control-flow or workload-distribution changes.

## Build Workflow

Collect several equal-duration production CPU profiles from representative
instances or windows. Merge them when that better represents normal traffic:

```bash
go tool pprof -proto profile-a.pprof profile-b.pprof > default.pgo
```

Unequal-duration profiles implicitly carry different weights. Use that only
when the weighting is intentional and documented.

Build comparison binaries from the same revision and toolchain:

```bash
go build -pgo=off -o "$ART/app-no-pgo" ./cmd/app
go build -pgo="$ART/default.pgo" -o "$ART/app-pgo" ./cmd/app
```

For an accepted profile committed beside the main package, `go build` uses
`default.pgo` through the default `-pgo=auto`; keep an explicit `-pgo=off`
comparison command in benchmark and incident runbooks.

## Evidence Matrix

Measure both binaries with the same workload, inputs, environment, warmup,
duration, and repetition count. Include:

| Evidence | Required comparison |
|---|---|
| CPU/service metric | CPU per request, throughput at fixed CPU, or latency at fixed load |
| Protected paths | representative success, miss, error, narrow, wide, encode, and decode paths |
| Compiler output | PGO inlining/devirtualization/block-layout decisions for named hot owners |
| Binary/build cost | binary bytes and clean build duration |
| Memory | `B/op`, `allocs/op`, RSS/heap, and GC where relevant |
| Correctness | normal test, race, deterministic-output, and wire/storage suites |

PGO can improve inlining, devirtualization, branch layout, and hot-code
placement. Do not infer any one of those effects from elapsed time alone;
inspect compiler diagnostics, profiles, or disassembly for the named owner.

Evaluate PGO as a separate whole-program candidate after accepted source-level
changes. At minimum compare:

1. baseline source with `-pgo=off`;
2. optimized source with `-pgo=off`;
3. optimized source with the representative profile;
4. protected holdout/minority workloads not dominant in the profile.

This separates source wins from compiler-profile wins and catches cases where
PGO amplifies a benchmark-specific path while moving cost into a protected
path. Follow
[experiment-framework.md](experiment-framework.md) for candidate combination
and regression budgets.

## Acceptance

Accept PGO only when:

- the profile represents the deployed workload rather than the evaluation set
  alone;
- evaluation includes a holdout traffic window or workload mix not used to tune
  source candidates or select the profile;
- the primary application metric improves reproducibly;
- protected minority and failure paths have no unacceptable regression;
- allocation, wire, determinism, and storage contracts remain unchanged;
- binary-size, build-time, profile-refresh, and rollout costs are documented;
- the non-PGO build remains available for comparison and rollback.

Reject or retrain when one benchmark family improves while another protected
family regresses, when the profile is benchmark-only without a production
proxy rationale, or when a profile from a dependency/library is proposed as a
whole-application default.

Cloudflare's published rollout is a useful production pattern: collect and
merge representative profiles, build with `-pgo`, then evaluate normalized CPU
over a sufficiently long deployment window. Its reported gain is evidence for
that workload, not a universal expected percentage.

Profile age is a production input. Record the source revision, collection
window, fleet/CPU class, traffic mix, and profile hash. Retrain or reject the
profile when the hot call graph, deployment architecture, or workload mix has
materially changed; do not silently keep an old profile because the build still
accepts it.

## Report Shape

Report:

- executable and profile owner;
- collection source, duration, merge/weighting, and profile age;
- exact `-pgo=off` and `-pgo=<profile>` build commands;
- before/after application and protected-path matrices;
- compiler/profile evidence for the changed hot owners;
- build time and binary size;
- accepted regressions or rejection reason;
- refresh, rollout, rollback, and profile-data handling policy.
