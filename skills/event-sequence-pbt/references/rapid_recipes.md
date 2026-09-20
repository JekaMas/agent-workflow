# Rapid Recipes For Event-Sequence PBT

Use these recipes after properties and events are defined. Do not start with a
rapid API choice; start with the boundary, properties, events, and fakes.

## Contents

- [Recipe index](#recipe-index)
- [Constructor-backed domain value](#1-constructor-backed-domain-value)
- [Struct payload with field overrides](#2-struct-payload-with-field-overrides)
- [Positive and negative event draw](#3-positive-and-negative-event-draw)
- [Action state machine with `Repeat`](#4-action-state-machine-with-repeat)
- [Method-based state machine](#5-method-based-state-machine)
- [Fake with calls, latency, and spam budgets](#6-fake-with-calls-latency-and-spam-budgets)
- [Regression from minimized sequence](#7-regression-from-minimized-sequence)
- [Fuzz handoff](#8-fuzz-handoff)
- [Review checklist](#review-checklist)

## Recipe Index

| Need | Use |
|---|---|
| Generate plain exported payload structs | `rapid.Make[T]` |
| Generate mostly automatic structs with constrained fields | `rapid.MakeCustom[T]` with `Fields` |
| Generate constructor-only domain values | explicit `rapid.Custom` or `MakeCustom` `Types` override that calls constructors |
| Generate valid/invalid event sequences from model context | explicit stateful generator |
| Test action preconditions and invariant checks after each step | `t.Repeat(map[string]func(*rapid.T){...})` |
| Keep larger action sets organized | `rapid.StateMachineActions(sm)` |
| Reuse the same property as Go fuzz entrypoint | `rapid.MakeFuzz(prop)` |
| Preserve a found bug | minimized deterministic regression test |

## 1. Constructor-Backed Domain Value

Use for typed identities, statuses, epochs, versions, amounts, keys, and other
values that must not be normalized after construction.

```go
func genRequestID() *rapid.Generator[RequestID] {
    return rapid.Custom(func(t *rapid.T) RequestID {
        raw := rapid.StringMatching(`[a-z][a-z0-9-]{0,31}`).Draw(t, "request_id_raw")
        id, err := NewRequestID(raw)
        if err != nil {
            t.Fatalf("generator produced invalid RequestID %q: %v", raw, err)
        }
        return id
    })
}
```

Rule: the generator may shape input, but the constructor remains the authority.

## 2. Struct Payload With Field Overrides

Use when most fields can be reflection-generated but some need narrower
domains.

```go
var eventPayloadGen = rapid.MakeCustom[EventPayload](rapid.MakeConfig{
    Types: map[reflect.Type]*rapid.Generator[any]{
        reflect.TypeOf(RequestID{}): genRequestID().AsAny(),
    },
    Fields: map[reflect.Type]map[string]*rapid.Generator[any]{
        reflect.TypeOf(EventPayload{}): {
            "Kind": rapid.SampledFrom([]EventKind{
                EventSubmit,
                EventCommit,
                EventDependencyReturns,
                EventDependencyFails,
            }).AsAny(),
            "Latency": rapid.Map(rapid.IntRange(0, 250), func(ms int) LogicalDuration {
                return LogicalDuration(ms)
            }).AsAny(),
        },
    },
})
```

Rules:

- use `Types` for exact concrete domain types;
- use `Fields` for one field on one exported struct type;
- use `Kinds` only when every value of that reflection kind can share the same
  generator;
- do not use `Make[T]` alone for domain types with private invariants.

## 3. Positive And Negative Event Draw

Use a model-aware generator to mix valid progress events with invalid/adversarial
attempts.

```go
func drawEvent(t *rapid.T, m Model) Event {
    kinds := []EventKind{EventTimeAdvances, EventProcessRestarts}

    if m.CanSubmit() {
        kinds = append(kinds, EventSubmit)
    }
    if m.HasPending() {
        kinds = append(kinds, EventCommit, EventCommitAbort)
    }
    if m.HasCommitted() {
        kinds = append(kinds, EventDependencyReturns, EventDependencyFails)
    }

    // Negative events stay in the same generator so shrinking can find minimal
    // bad interleavings.
    kinds = append(kinds,
        EventWrongOwnerResult,
        EventDuplicateResult,
        EventOldEpochResult,
        EventMalformedPayload,
        EventUnauthorizedCommand,
    )

    return Event{
        Kind: rapid.SampledFrom(kinds).Draw(t, "kind"),
        ID:   drawPossiblyRelatedID(t, m),
        Body: eventPayloadGen.Draw(t, "payload"),
    }
}
```

Rules:

- draw from the model context, not from SUT internals;
- generate invalid events intentionally;
- keep positive events frequent enough to make progress;
- assert properties after every event.

## 4. Action State Machine With `Repeat`

Use when actions have preconditions and each accepted action should run an
invariant check.

```go
func TestQueueStateMachine(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        limit := rapid.IntRange(1, 32).Draw(t, "limit")
        sut := NewQueue(limit)
        model := make([]int, 0, limit)

        t.Repeat(map[string]func(*rapid.T){
            "put": func(t *rapid.T) {
                if len(model) == limit {
                    t.Skip("queue full")
                }
                v := rapid.Int().Draw(t, "value")
                sut.Put(v)
                model = append(model, v)
            },
            "get": func(t *rapid.T) {
                if len(model) == 0 {
                    t.Skip("queue empty")
                }
                got := sut.Get()
                want := model[0]
                model = model[1:]
                if got != want {
                    t.Fatalf("got %d, want %d", got, want)
                }
            },
            "": func(t *rapid.T) {
                if sut.Size() != len(model) {
                    t.Fatalf("size mismatch: got %d, want %d", sut.Size(), len(model))
                }
            },
        })
    })
}
```

Rules:

- use `t.Skip` only for an inapplicable generated action, with disposition
  `skipped_precondition`; it never counts as exercised coverage. When invalid
  placement or rejection is required, call the SUT in a separate action and
  assert the expected rejection and forbidden mutations;
- never mutate setup state just to make an action valid;
- put invariant checks under key `""`;
- use fake counters inside the invariant action.

## 5. Method-Based State Machine

Use when action maps become large.

```go
type lifecycleSM struct {
    model Model
    sut   *Harness
}

func (sm *lifecycleSM) Check(t *rapid.T) {
    assertVisibleState(t, sm.model, sm.sut)
    assertCounters(t, sm.model, sm.sut.Counters())
}

func (sm *lifecycleSM) Submit(t *rapid.T) {
    ev := drawSubmitEvent(t, sm.model)
    sm.apply(t, ev)
}

func (sm *lifecycleSM) DependencyFails(t rapid.TB) {
    ev := drawDependencyFailureEvent(t, sm.model)
    sm.apply(t, ev)
}

func TestLifecycleStateMachine(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        sm := newLifecycleSM(t)
        t.Repeat(rapid.StateMachineActions(sm))
    })
}
```

Rules:

- `Check(*rapid.T)` is required;
- public action methods may accept `*rapid.T` or `rapid.TB`;
- keep action methods thin: draw event, apply to model and SUT, assert step
  result.

## 6. Fake With Calls, Latency, And Spam Budgets

Use for external dependencies, queues, clocks, storage, or worker pools.

```go
type CountingFake struct {
    Calls   map[string]int
    Logs    map[string]int
    Latency map[string]LogicalDuration
    LockedCalls int
}

func (f *CountingFake) Call(method string, latency LogicalDuration, lockHeld bool) {
    f.Calls[method]++
    f.Latency[method] += latency
    if lockHeld {
        f.LockedCalls++
    }
}

func (f *CountingFake) AssertBudgets(t rapid.TB, b Budgets) {
    for method, maxCalls := range b.MaxCalls {
        if f.Calls[method] > maxCalls {
            t.Fatalf("%s calls=%d > max=%d", method, f.Calls[method], maxCalls)
        }
    }
    if f.LockedCalls != 0 {
        t.Fatalf("external calls while lock held: %d", f.LockedCalls)
    }
}
```

Rules:

- count every external call, even failed or cancelled calls;
- add logical latency to the fake, not sleeps;
- assert budgets after every event/action;
- include log counters for spam properties.

## 7. Regression From Minimized Sequence

Use when rapid finds a real bug.

```go
func TestLifecycle_MinimizedRegression(t *testing.T) {
    events := []Event{
        {Kind: EventSubmit, ID: mustID("a")},
        {Kind: EventCommit, ID: mustID("a")},
        {Kind: EventDependencyFails, ID: mustID("a")},
        {Kind: EventTimeAdvances, Advance: 1},
        {Kind: EventDependencyFails, ID: mustID("a")},
    }

    h := NewHarness()
    m := NewModel()
    for i, ev := range events {
        expected := m.Apply(ev)
        actual := h.Apply(ev)
        assertStep(t, i, events, expected, actual)
        assertProperties(t, i, events, m, h)
    }
}
```

Rules:

- keep the minimized sequence as data, not prose;
- assert the same properties as the PBT;
- name the regression after the property that failed.

## 8. Fuzz Handoff

Use when the same property should also be an external-boundary fuzz target.

```go
func lifecycleProperty(t *rapid.T) {
    model := NewModel()
    h := NewHarness()
    eventCount := rapid.IntRange(1, 200).Draw(t, "event_count")

    for i := 0; i < eventCount; i++ {
        ev := drawEvent(t, model)
        expected := model.Apply(ev)
        actual := h.Apply(ev)
        assertStep(t, i, nil, expected, actual)
        assertProperties(t, i, nil, model, h)
    }
}

func TestLifecycleProperties(t *testing.T) {
    rapid.Check(t, lifecycleProperty)
}

func FuzzLifecycleProperties(f *testing.F) {
    f.Fuzz(rapid.MakeFuzz(lifecycleProperty))
}
```

Rules:

- use this only when fuzzing is meaningful for the boundary;
- keep panic-free and deterministic error behavior as explicit properties;
- still keep deterministic regression tests for minimized failures.

## Review Checklist

- Does every recipe start from properties and event semantics?
- Are constructor-only values produced through constructors?
- Are invalid events generated deliberately?
- Are fake call, log, latency, lock, retry, and queue counters asserted?
- Are liveness properties paired with fairness assumptions?
- Are found bugs preserved as deterministic regression sequences?
