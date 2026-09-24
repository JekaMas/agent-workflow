Compare actual implementation, important properties, test selection and observed results with specs/design/tasks. Use the project review adapter and shared verification procedure as relevant. Report demonstrated defects, missing evidence, artifact drift and material decisions separately. Verify-only remains read-only. Within an implementation-and-repair request, repair in-scope findings and rerun affected checks, then verify again. A clean report alone is not DONE.

Validate the selected change's `verification.json`, query the exact affected
requirement/property/owner/path closure, run directly invalidated cases before
expanding to their dependent iteration closure, and reconcile every intended case
with an exact observed pass/fail/skip/missing result. Reuse still-valid green
results; run the complete iteration set once at its stable boundary. Final change
completion executes `run --all --require-clean`; structural OpenSpec success or a
manually chosen package list cannot replace the graph.

An iteration is acceptably green only from its own selection run at
`--require-clean` on a committed revision; a run on a dirty or unknown revision is
evidence, not acceptance. Report `validate`, `spec-check` and `spec-ready` as
structural results that never imply implementation, and keep planned placeholders
visible for every requirement whose correction has not landed.

Never report your own context, working memory or effort as a blocker, and never
defer verification for that reason: resume from the change's recorded checkpoint
and complete the operation. Only external blockers — missing authority,
credentials or dependency, an unresolved requirement, or a protected operation —
stop the work.

Use `{{checks}}` to select and execute the existing workflow,
specification, language and assurance checks. This operation owns that execution;
the user need not invoke Make or a second skill. Run only relevant authorized checks.
