Resolve the requested check and its actual target from the request/current change.
Execute the selected existing command within authority; inspect exit status,
selected/executed cases and evidence. Do not merely print a command when execution
was requested. If no selector is given, choose checks from the actual diff and
acceptance criteria; do not run the whole catalog. Ask only for unresolved target
ambiguity or missing authority after independent work.
A standalone check reports findings; existing implementation authority continues
through repair and affected revalidation. Checks alone never mark tasks DONE.

For behavioral OpenSpec work, `spec` validates the complete evidence DAG,
`spec-tests` executes a nonempty affected closure selected by requirement,
property, owner or changed path, and `ready` executes the complete required DAG
with the evidence tool's `run --all` operation.
Report intended and observed exact test identities; a zero selection is failure.
