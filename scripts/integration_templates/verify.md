Compare actual implementation, important properties, test selection and observed results with specs/design/tasks. Use the project review adapter and shared verification procedure as relevant. Report demonstrated defects, missing evidence, artifact drift and material decisions separately. Verify-only remains read-only. Within an implementation-and-repair request, repair in-scope findings and rerun affected checks, then verify again. A clean report alone is not DONE.

Validate the selected change's `verification.json`, query the exact affected
requirement/property/owner/path closure, execute that closure, and reconcile every
intended case with an exact observed pass/fail/skip/missing result. Final completion
verification executes `run --all`; structural OpenSpec success or a manually
chosen package list cannot replace the graph.

Use `{{checks}}` to select and execute the existing workflow,
specification, language and assurance checks. This operation owns that execution;
the user need not invoke Make or a second skill. Run only relevant authorized checks.
