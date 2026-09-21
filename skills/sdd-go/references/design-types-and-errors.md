# Design, Types, And Errors

Load this reference for Go package/API design, refined domain values, method
sets, interfaces, and returned errors.

## Package And API Design

- Keep one behavior owner per cohesive package/file. Prefer small structs,
  explicit dependencies, composition, and consumer-defined narrow interfaces.
- Export only stable supported behavior. Avoid premature interfaces, helper
  explosions, framework layers, and god types.
- Choose receivers intentionally: value receivers for small immutable values;
  pointer receivers for mutation, identity, or expensive copies. Keep method
  sets consistent and review interface satisfaction when adding methods.
- Use interfaces for a real boundary or polymorphism, not merely to mock one
  call. Prefer an existing concrete seam such as `http.RoundTripper` when it is
  sufficient.

## Canonical Domain Types

Before adding a type, inspect relevant `types.go` files and reuse the existing
canonical concept if possible.

- Construct refined values at API/config/DB/parser/adapter boundaries.
- Keep internal fields unexported and expose a minimal constructor plus one
  canonical accessor.
- Define normalization, charset, length, case, encoding, and unit invariants.
- Copy input bytes when later mutation could invalidate the value.
- Keep construction deterministic and idempotent; return stable typed errors.
- Do not bypass constructors with casts, literals, or direct structs outside an
  explicit allowlisted definition/test path.
- Implement boundary serialization interfaces when they own strict decoding;
  do not add convenience parse/marshal methods without a real consumer.
- Add fuzz/round-trip/immutability tests when constructor or decode behavior
  changes.
Example:

```go
type ItemID struct{ value string }

func ParseItemID(raw string) (ItemID, error) {
    // Normalize and validate once at the boundary.
}

func (id ItemID) String() string { return id.value }
```

## Errors

Follow the consumer's stable error taxonomy. Preserve error identity when wrapping,
add safe operation context at a meaningful boundary and do not discard errors or
replace failures with favorable defaults. Keep secrets out of error messages.
No particular SDK error type, sentinel representation or correlation field is
required by this shared reference.

## Generics

Use generics when they remove demonstrated duplication or strengthen a type
invariant. Escalate from function, to methods, to generics, and only then to an
interface when runtime polymorphism is actually required. Keep constraints
simple and verify hot-path abstractions through the performance workflow rather
than speculation.
