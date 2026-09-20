# Event-Sequence PBT Examples

These snippets are templates. Rename events, identities, and fakes to the
feature domain.

## Contents

- [Event definitions](#event-definitions)
- [Model handler](#model-handler)
- [Counting fake with logical latency](#counting-fake-with-logical-latency)
- [SUT handler](#sut-handler)
- [Stateful generator](#stateful-generator)
- [`rapid.Make[T]` for event payloads](#rapidmaket-for-event-payloads)
- [Rapid state machines](#rapid-state-machines)
- [Property assertions](#property-assertions)
- [Reproducible failure output](#reproducible-failure-output)

## Event Definitions

```go
type EventKind uint8

const (
    EventSubmitCommand EventKind = iota
    EventCommitAccepted
    EventCommitAborted
    EventDependencyReturns
    EventDependencyFails
    EventTimeAdvances
    EventProcessRestarts
    EventDuplicateResult
)

type Event struct {
    Kind     EventKind
    ID       ID
    Epoch    Epoch
    Payload  Payload
    Advance  Duration
}
```

Events are "what happened". They are not cache mutations.

## Model Handler

```go
type Model struct {
    Now      Duration
    Items    map[ID]ItemState
    Expected Counters
}

func (m *Model) Apply(ev Event) Step {
    switch ev.Kind {
    case EventSubmitCommand:
        if _, exists := m.Items[ev.ID]; exists {
            return Step{Result: Duplicate}
        }
        m.Items[ev.ID] = ItemState{Phase: Pending}
        return Step{Result: Accepted}
    case EventCommitAccepted:
        item, ok := m.Items[ev.ID]
        if !ok || item.Phase != Pending {
            return Step{Result: Rejected}
        }
        item.Phase = Committed
        m.Items[ev.ID] = item
        return Step{Result: Accepted}
    case EventDependencyReturns:
        item, ok := m.Items[ev.ID]
        if !ok || item.Phase != Committed {
            return Step{Result: Rejected}
        }
        if ev.Epoch.LessThan(item.Epoch) {
            return Step{Result: Duplicate}
        }
        item.Phase = Terminal
        item.Epoch = ev.Epoch
        m.Items[ev.ID] = item
        return Step{Result: Accepted}
    case EventTimeAdvances:
        m.Now += ev.Advance
        return Step{Result: Accepted}
    default:
        return Step{Result: Rejected}
    }
}
```

## Counting Fake With Logical Latency

```go
type CountingFake struct {
    Calls        map[string]int
    Latency      map[string]Duration
    Forbidden    int
    LockHeld     int
    NextResponse Response
}

func (f *CountingFake) Call(method string, id ID, lockHeld bool) Response {
    if lockHeld {
        f.LockHeld++
    }
    f.Calls[method]++
    f.Latency[method] += f.NextResponse.Latency
    return f.NextResponse
}

func (f *CountingFake) AssertLocalOnly(t require.TestingT) {
    require.Zero(t, f.Forbidden)
    require.Zero(t, f.LockHeld)
    for method, calls := range f.Calls {
        require.Zerof(t, calls, "unexpected external call %s", method)
    }
}
```

## SUT Handler

```go
type Harness struct {
    SUT   *Engine
    Fake  *CountingFake
    Clock *LogicalClock
}

func (h *Harness) Apply(ev Event) ActualStep {
    switch ev.Kind {
    case EventSubmitCommand:
        return h.SUT.Submit(ev.ID, ev.Payload)
    case EventCommitAccepted:
        return h.SUT.ApplyCommitted(ev.ID)
    case EventDependencyReturns:
        h.Fake.NextResponse = Response{Value: ev.Payload, Latency: ev.Advance}
        return h.SUT.ObserveResult(ev.ID, ev.Epoch)
    case EventTimeAdvances:
        h.Clock.Advance(ev.Advance)
        return ActualStep{Result: Accepted}
    case EventProcessRestarts:
        h.SUT = RestartFromPersistentState(h.SUT.PersistentState(), h.Fake, h.Clock)
        return ActualStep{Result: Accepted}
    default:
        return h.SUT.ApplyInvalidAttempt(ev)
    }
}
```

## Stateful Generator

```go
func drawEvent(rt *rapid.T, m Model) Event {
    choices := []EventKind{
        EventSubmitCommand,
        EventTimeAdvances,
        EventProcessRestarts,
    }
    if m.HasPending() {
        choices = append(choices, EventCommitAccepted, EventCommitAborted)
    }
    if m.HasCommitted() {
        choices = append(choices, EventDependencyReturns, EventDependencyFails)
    }
    if m.HasTerminal() {
        choices = append(choices, EventDuplicateResult)
    }

    kind := rapid.SampledFrom(choices).Draw(rt, "kind")
    return Event{
        Kind:    kind,
        ID:      drawID(rt),
        Epoch:   drawEpoch(rt),
        Payload: drawPayload(rt),
        Advance: drawDuration(rt),
    }
}
```

## `rapid.Make[T]` For Event Payloads

Use `rapid.Make[T]` for simple exported test payload structs. Use
`rapid.MakeCustom[T]` when a field, type, or kind needs a narrower generator.
Do not use reflection generation to bypass constructor-only domain invariants;
for those types, provide a custom generator that calls the constructor.
The override maps use `reflect.Type` and `reflect.Kind`.

```go
type Payload struct {
    ID      ID
    Kind    EventKind
    Advance Duration
    Note    string
}

var payloadGen = rapid.MakeCustom[Payload](rapid.MakeConfig{
    Types: map[reflect.Type]*rapid.Generator[any]{
        reflect.TypeOf(ID{}): rapid.Custom(func(t *rapid.T) ID {
            raw := rapid.StringMatching(`[a-z][a-z0-9]{0,7}`).Draw(t, "id")
            id, err := NewID(raw)
            if err != nil {
                t.Fatalf("generator produced invalid ID %q: %v", raw, err)
            }
            return id
        }).AsAny(),
    },
    Fields: map[reflect.Type]map[string]*rapid.Generator[any]{
        reflect.TypeOf(Payload{}): {
            "Kind": rapid.SampledFrom([]EventKind{
                EventSubmitCommand,
                EventCommitAccepted,
                EventDependencyFails,
            }).AsAny(),
            "Advance": rapid.Map(rapid.IntRange(0, 10_000), func(ms int) Duration {
                return Duration(ms)
            }).AsAny(),
        },
    },
})

func drawPayload(t *rapid.T) Payload {
    return payloadGen.Draw(t, "payload")
}
```

Rules:

- `Types` overrides every occurrence of an exact concrete type.
- `Fields` overrides named exported fields for one struct type.
- `Kinds` can narrow all values of a reflection kind, such as all strings.
- Private fields are ignored by `Make`; use type overrides when private state
  must be constructed through a validated constructor.

## Rapid State Machines

Use `t.Repeat` when the SUT has actions with preconditions and invariants that
must be checked before and after every accepted action. An inapplicable
generated action may call `t.Skip(...)` without counting as coverage. Required
invalid-input/rejection actions must invoke the SUT and assert their
`observed_no_mutation` contract; never mutate setup state to force validity.

```go
func TestQueueEventStateMachine(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        maxSize := rapid.IntRange(1, 32).Draw(t, "max_size")
        q := NewQueue(maxSize)
        model := make([]int, 0, maxSize)

        t.Repeat(map[string]func(*rapid.T){
            "put": func(t *rapid.T) {
                if len(model) == maxSize {
                    t.Skip("queue full")
                }
                v := rapid.Int().Draw(t, "value")
                q.Put(v)
                model = append(model, v)
            },
            "get": func(t *rapid.T) {
                if len(model) == 0 {
                    t.Skip("queue empty")
                }
                got := q.Get()
                want := model[0]
                model = model[1:]
                if got != want {
                    t.Fatalf("got %d, want %d", got, want)
                }
            },
            "": func(t *rapid.T) {
                if q.Size() != len(model) {
                    t.Fatalf("size mismatch: got %d, want %d", q.Size(), len(model))
                }
            },
        })
    })
}
```

For larger state machines, wrap actions as methods and use
`rapid.StateMachineActions`.

```go
type queueSM struct {
    q     *Queue
    model []int
    limit int
}

func (sm *queueSM) Check(t *rapid.T) {
    if sm.q.Size() != len(sm.model) {
        t.Fatalf("size mismatch: got %d, want %d", sm.q.Size(), len(sm.model))
    }
}

func (sm *queueSM) Put(t *rapid.T) {
    if len(sm.model) == sm.limit {
        t.Skip("queue full")
    }
    v := rapid.Int().Draw(t, "value")
    sm.q.Put(v)
    sm.model = append(sm.model, v)
}

func (sm *queueSM) Get(t rapid.TB) {
    if len(sm.model) == 0 {
        t.Skip("queue empty")
    }
    got := sm.q.Get()
    want := sm.model[0]
    sm.model = sm.model[1:]
    if got != want {
        t.Fatalf("got %d, want %d", got, want)
    }
}

func TestQueueStateMachineActions(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        limit := rapid.IntRange(1, 32).Draw(t, "limit")
        sm := &queueSM{q: NewQueue(limit), limit: limit}
        t.Repeat(rapid.StateMachineActions(sm))
    })
}
```

State-machine properties to assert with typed disposition counters:

- skipped preconditions do not count as coverage;
- generated invalid actions invoke the SUT and count as
  `observed_no_mutation` only after the expected rejection and forbidden
  mutations are asserted;
- every accepted action is followed by invariant checks;
- external fake call counts respect per-action budgets;
- logical latency remains within the property bound after every action.

## Property Assertions

```go
func assertProperties(t *rapid.T, events []Event, model Model, h *Harness) {
    require.Equal(t, model.VisibleState(), h.SUT.VisibleState())
    require.LessOrEqual(t, h.Fake.Calls["remote.read"], model.Expected.Calls["remote.read"])
    require.Zero(t, h.Fake.Forbidden)
    require.Zero(t, h.Fake.LockHeld)
    require.LessOrEqual(t, h.Clock.PhaseLatency(), model.Expected.MaxLatency)
    require.LessOrEqual(t, h.SUT.QueueLen(), model.Expected.MaxQueue)
}
```

Assert after every event, not only at the end.

The abbreviated queue example uses `t.Skip` only to keep Rapid from choosing an
inapplicable action. A required empty-queue read/rejection property needs a
separate generated action that calls the production boundary and asserts its
`observed_no_mutation` contract.

## Reproducible Failure Output

```go
func failWithTrace(t *rapid.T, index int, events []Event, model Model, h *Harness, msg string) {
    t.Fatalf("%s\nindex=%d\nevents=%#v\nmodel=%#v\nsut=%#v\ncounters=%#v\nlogical_time=%s",
        msg,
        index,
        events,
        model.Summary(),
        h.SUT.Summary(),
        h.Fake,
        h.Clock.Now(),
    )
}
```

When the minimized sequence describes a real issue, add it as a deterministic
regression test beside the property test.
