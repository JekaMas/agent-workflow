# Language and framework adapters

The event/model/oracle contract is independent of the implementation language.
Select the project's existing framework and inspect supported generation,
state-machine execution, shrinking, persistence and replay behavior. Do not add a
framework just to follow this skill. Return evidence to the existing task list.

| Context | Relevant adaptation |
|---|---|
| Go with Rapid | Use rapid_recipes.md and the Go examples only when Rapid is already selected. A testing.Short skip requires a separate executed selector if the property is required. Preserve GOWORK/module selection and failing seeds. |
| Rust with Proptest or another selected tool | Represent events as typed values; preserve causal validity or intentional rejection during shrinking. Record the persisted regression, seed when available, manifest, Cargo target, features and arithmetic assumptions. Do not assume a Go Repeat API or identical shrink behavior. |
| Other languages | Map typed event/disposition concepts to the language's data types and existing framework; inspect its actual replay and shrinking semantics. A generic event-list generator can drive an independent model without a dedicated state-machine API. |
| Mixed-language boundary | Feed a common serialized trace into independent adapters; state integer widths, serialization/errors and projected observations. One adapter's agreement with itself is not cross-language conformance. |

A seed alone may not replay across framework/toolchain revisions. Retain the
minimized concrete event trace and relevant configuration. Shrinking must preserve
the failure and meaningful causal/rejection conditions. If shrinking is unavailable,
record that limit and minimize a deterministic trace explicitly where practical.

Logical time tests model deadlines, not hardware performance or every concurrent
schedule. Real I/O/recovery and concurrency checks have separate assumptions and
observations. Do not discard them merely because the deterministic model passes.
