# Local extraction validation

The shared parser/process/native OpenSpec suite passed 40/40 with OpenSpec 1.13.1.
A consumer run passed 41/41: the shared cases plus its own Make selector contract,
using the consumer's OpenSpec configuration. Both skill entrypoints passed the
installed skill packaging validator.

Review detected and repaired a Make adapter error that removed the trailing dollar
anchor from a Go selector. The existing regression rejected it before acceptance.

The disposable planning/implementation rehearsal used OpenSpec 1.13.1 and Go
1.26.5. It created native change metadata, retrieved proposal/spec/design/task/apply
instructions, authored requirements and an oracle plan, then implemented a clamp:

- incomplete implementation: actual behavior tests failed;
- correct implementation: all three top-level tests passed, including two sets of
  1000 deterministic property samples and nine fixed boundary/rejection vectors;
- deliberately wrong high-bound branch: actual behavior tests failed;
- restored implementation: required tests passed;
- absent test selector: rejected as missing evidence;
- completed native change: structural/guidance/task readiness passed.

An initial attempt inherited a mismatched GOROOT and failed to compile. It was
classified as environment failure, not behavioral red. The rehearsal now lets the
explicitly selected binary determine its own GOROOT and requires named behavioral
failures rather than accepting any nonzero exit. Only its subprocess environment
changes; global configuration is untouched. Initial failure artifacts were retained
by the consuming project.

Selected fixture inputs measured 168 bytes initially, 40,338 planning bytes
(including full reference documents and native instruction responses), and 3,819
implementation bytes (apply response and selected artifacts). These are UTF-8 source
sizes, not model tokens. The script is a same-session deterministic rehearsal;
it does not establish fresh-agent instruction following, context selection quality,
or defect-detection improvement. Run it with a new output directory to retain
exact inputs, results and per-stage file identities on your machine.
