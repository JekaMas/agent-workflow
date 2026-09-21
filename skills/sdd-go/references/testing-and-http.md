# Go HTTP seams and boundary testing

Use the existing assertion conventions and toolchain. Test helpers, context APIs
and skip policy remain consumer-owned.

## Outbound HTTP

Use the existing boundary in this order:

1. existing service/client interface;
2. injected `*http.Client` with a deterministic `RoundTripper`;
3. a real listener only when socket/server integration is itself under test.

Do not add a one-use interface when `RoundTripper` is sufficient. Do not mutate
`http.DefaultTransport` or rely on shared global HTTP state.

```go
type roundTripFunc func(*http.Request) (*http.Response, error)

func (fn roundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) {
    return fn(req)
}
```

Assert method, path, headers, safe body fields, and deterministic response
handling without real network IO.

## Fuzzing And Boundary Tests

- Seed valid and malformed inputs.
- Assert no panic, deterministic error class, resource bounds, and round-trip
  invariants where applicable.
- Keep fuzz inputs at the actual untrusted decode/validation boundary.
- Add explicit negatives for missing/invalid fields, wrong ownership, bad
  lengths/encodings, and corrupted storage payloads where relevant.

