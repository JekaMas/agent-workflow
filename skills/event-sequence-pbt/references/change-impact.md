# Property-suite change impact

Use when state/transition/model/harness changes can invalidate an existing property set. Map important deltas to retained/new properties and actual focused/broader commands; consumer policy owns the fast gate and exact full-suite selection.

| Changed event/transition/invariant/owner | Existing property IDs | New or amended property | Focused command | Full local command/owner; existing CI if applicable |
|---|---|---|---|---|

Use the mapping as follows:

- add a domain event only when production adds a reachable occurrence or
  changes its prerequisites or rejection contract;
- add or amend a property only when an invariant, fairness assumption, bound,
  ordering rule, or forbidden side effect changes;
- run the affected property selector when it is the useful discriminator;
  preserve deterministic regression and broader required checks;
- run the full dedicated PBT suite when shared event vocabulary, model/oracle,
  harness, registry, or production-owner semantics change; and
- preserve a deterministic regression in the ordinary regression gate for every
  confirmed property failure.
