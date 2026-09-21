# Local runner selection limits

Read when selecting a shared language adapter, rather than native project checks.

The selected wrapper preserves the literal regex argument. The Go helper requires an
anchored top-level test selector (no `/`) and a nonempty resolved package set;
every selected package must execute tests, with no required skips. Selecting a
parent runs its real children. Slash/subtest selectors are explicitly unsupported
because a passing parent does not prove the requested child ran; use a native
command with inspected exact leaf evidence for that requirement, not a weaker
parent-only substitute. Use native Go JSON output to confirm the exact child;
`-list` cannot establish child execution. The helper already uses `-count=1`.
Use the existing supported Go
binary via PATH or the helper's `--tool` option: GOTOOLCHAIN=local prevents an
implicit download. Package-specific build tags/features or unusual selections
not exposed by this small adapter need an explicit native command and evidence;
do not silently substitute the default configuration.

Heavy optional adapter experiments remain separate from quick workflow checks:
`python3 -B .agents/workflow/scripts/test_local_verify_go.py --go-tool <existing-go> --output-dir <new-dir>`
and `python3 -B .agents/workflow/scripts/test_local_verify_cargo.py --output-dir <new-dir>`.
They use only disposable synthetic packages/crates and never prove product
behavior. The Go experiment has eight expected outcome cases; Cargo has four. Product Go/Rust tests are selected only for their
actual change risk. Inspect actual live-call gates before selecting Rust tests: Cargo offline resolution does not prevent test network calls.

