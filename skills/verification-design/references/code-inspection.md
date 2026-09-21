# Implementation inspection

Inspect the affected production owners/callers and related failure cases, not just the diff or a favorable test substitute. Review error identity, safe diagnostic context, numeric conversion/overflow, ordering where canonical output requires it, resource lifetime and cleanup under partial failure. Select domain contracts from the consumer rather than assuming financial units or a particular SDK.

Background work needs ownership, exit and observation; queues need bounded backlog/overflow semantics. Do not infer scheduler fairness, cleanup or liveness from a race pass. Retained buffers and leaked workers are correctness risks. Use measured evidence before cache/pool/runtime tuning. Keep new behavior with cohesive owners; generator changes are validated from canonical inputs. Preserve public behavior and keep unrelated cleanup out of scope.

For lifecycle classifiers, inspect paired positive/negative cases crossing delayed first use, owner replacement/removal, restart/reopen, pruning and relevant ordering. A timestamp/proxy needs evidence of equivalence to the authoritative fact. Inspect interacting requirements and resource cardinalities, not just individually green tests.

Reuse evidence only when its relevant dependency closure is unchanged. Qualify a discriminator for a demonstrated repair without manufacturing failure in correct code. In review-only scope propose the missing test; in authorized implementation create/repair/revalidate it in the same change. Resolve findings by severity and report exact evidence, remaining gaps and unblock actions. Required product-specific or operational evidence cannot be replaced by a clean code review.
