# Rust boundaries and resources

Keep transport decoding, validation/authorization, domain operations and safe
response mapping explicit. Use typed values where they enforce the actual contract;
retain the consumer's serialization, numeric and API semantics. Do not impose a
particular web framework, wallet provider or signing protocol.

Reject invalid inputs before side effects. Bound response reads and background
work, preserve every meaningful Result, and classify external failures without
exposing arbitrary sensitive bodies. Use existing error conventions; a new error
crate requires a concrete consumer benefit rather than style preference.

Keep shared state immutable where practical and share only actual dependencies.
Resource/task lifetime must remain correct under cancellation and failure. For
canonical bytes or signing, specify ordering, units, rounding/overflow and nonce
semantics, then check independent vectors. Those contracts come from the product;
not every Rust application requires deterministic serialization or fixed-point math.
