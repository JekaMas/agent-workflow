# Design

## Context

The current verification procedure recommends a requirement/property/test map,
but makes it optional and leaves commands in prose or chat history. OpenSpec
structural checks cannot tell whether affected tests were omitted, selected zero
cases, or failed in an unreported package. The shared local Go runner also forces
`GOTOOLCHAIN=local`, which can select an older host compiler even when an exact
newer toolchain is already cached.

## Goals / Non-Goals

**Goals:**

- One portable, machine-readable graph is the authoritative test selection map.
- Fast deterministic forward and reverse lookup supports incremental execution.
- Exact observed test identities, not command exit alone, establish execution.
- Positive and negative cases exist for every property and every spec scenario is
  covered.
- Commands are deduplicated and shared test edges remain explicit.
- Final readiness runs the complete required graph once on stabilized source.

**Non-Goals:**

- Inferring semantic properties from coverage percentages or source names.
- Automatically authorizing protected external tests.
- Replacing consumer-specific test runners, production oracles or commands.
- Treating structural manifest validation as behavioral evidence.

## Decisions

### 1. Store a versioned JSON evidence DAG beside each change

The canonical file is `openspec/changes/<change>/verification.json`. JSON keeps
the validator dependency-free and supports deterministic canonical hashing. Its
node sets are:

- `requirements`: stable consumer ID, capability path, exact requirement title,
  exact scenario titles and computed specification fingerprint;
- `properties`: stable ID, requirement/scenario edges, owner, statement, oracle,
  source/invalidation globs and case edges;
- `cases`: stable ID, polarity (`positive` or `negative`), exact observable,
  explicit covered scenario edges, expected test identity, command edge, implementation state, exact test-source
  path and SHA-256 fingerprint, and substitution disclosure;
- `commands`: canonical argv/cwd/environment/runner/timeout definition executed
  once for the selected case closure.

Alternative: prose tables in design/tasks. Rejected because they cannot reject
stale pins, zero selection, duplicated cases or unexecuted claims.

### 2. Fingerprint parsed specification points

The tool parses delta specs and hashes a canonical tuple of capability path,
requirement title, requirement body and ordered scenarios. Each requirement node
stores this SHA-256. Exact title/scenario matching plus the fingerprint makes
drift visible without inventing a second requirement ID syntax.

Alternative: hash whole spec files. Rejected because one unrelated requirement
edit would invalidate every case in the file and defeat incremental selection.

### 3. Build in-memory forward and reverse indexes

Validation constructs maps for requirement, scenario, property, case, exact test,
command, owner and normalized source glob. Query accepts any combination of
requirement IDs, property IDs, case IDs, exact tests, command IDs, owners or
changed paths and returns the detailed sorted unique transitive closure. Expected scale is small enough that rebuilding indexes from JSON is
faster and safer than committing generated indexes.

### 4. Reject true duplicates while preserving distinct protection

Within one property, `(polarity, observable, expected_test)` is unique. A command
definition is keyed by its canonical execution tuple; identical definitions must
share one command node. One observed test may support several properties only
through separate edges whose observables or failure classes differ. This follows
the strict overlap rule and prevents both duplicated execution and accidental
loss of distinct protection.

### 5. Observe test identities through runner adapters

The first implementation supports:

- `go-test-json`: injects `-json`, parses exact test/subtest pass/fail/skip events,
  and requires every selected expected identity to pass;
- `cargo-test`: parses exact libtest `test <name> ... ok|FAILED|ignored` records;
- `command`: requires explicit stable success markers for non-language structural
  checks and cannot satisfy a behavioral case without such a marker.

Commands are argv arrays and never shell-evaluated. Missing executable, timeout,
nonzero exit, missing expected identity, skip or fail is non-passing.

### 6. Separate structural, incremental and final commands

- `validate` checks the complete graph but executes nothing.
- `query` prints deterministic closure for review/search.
- `run --requirements/--properties/--owners/--changed-paths` requires nonempty
  selection and executes the affected closure.
- `run --all` executes every required implemented case and fails on planned or
  authority-blocked cases.

Apply and verify MUST call affected `run`; final readiness MUST call `run --all`.
Every scenario edge of every property requires both positive and negative cases;
a requirement-level property pair cannot silently stand in for an unlisted
scenario. An implemented case is valid only while its exact test-source file still matches
its pinned SHA-256. Planned or blocked cases retain their intended source path but
cannot pass. Result JSON records graph/spec/source hashes, Git HEAD and dirty state, requested
selectors, intended cases, observed test identities, commands, exits and gaps.

### 7. Let Go resolve an already-cached required toolchain offline

The shared Go runner stops forcing `GOTOOLCHAIN=local`. It uses `GOTOOLCHAIN=auto`
with `GOWORK=off`, `GOPROXY=off`, `GONOPROXY=none` and read-only module flags.
An already-cached toolchain can satisfy `go.mod`; an uncached toolchain or module
fails without network installation.

## Risks / Trade-offs

- **[Large existing changes need initial mapping work]** → Allow structurally
  complete `planned` cases during implementation, including an explicit
  `UNDECIDED` substitution boundary; selected/final execution treats them as
  incomplete, and implementation is invalid until the boundary is classified.
- **[One test contains several subcases]** → Store exact subtest identities when
  emitted; otherwise the parent can support multiple edges only with distinct
  observables and reviewable assertions.
- **[Source globs are too broad]** → Report why each case was selected and keep
  unrelated package membership out of the invalidation model.
- **[External cases cannot run locally]** → Keep their authority class and blocked
  status explicit; never auto-run or silently exclude them from required closure.
- **[Consumer pin update is interrupted]** → Shared branch/commit remains usable;
  consumers keep their previous exact pin until an explicit update validates.

## Migration Plan

1. Implement and test the shared graph tool and operation guidance.
2. Publish the shared branch and PR.
3. Update Smart Example's submodule pin and rendered integrations.
4. Add a complete GMX verification graph: future requirements may be `planned`,
   while the currently affected iteration-one nodes must be implemented and green.
5. Wire `spec-check`, affected `spec-tests`, and final `spec-ready` behavior.
6. Re-run the iteration-one requirement closure and correct its checkpoint record.

Rollback removes the consumer command wiring and returns the exact prior shared
pin; product tests and specifications remain intact.
