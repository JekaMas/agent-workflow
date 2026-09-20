For each newly introduced capability, supply a meaningful `## Purpose` before
synchronization; native archive can otherwise insert a placeholder that fails
strict main-spec validation. After sync/archive, run
`openspec validate <capability> --type spec --strict --json --no-interactive`
for every affected main spec, preserving the selected store/root. Inspect its
requirements, links and scenarios. A successful archive command alone is not
valid synchronization; repair any resulting spec defect and revalidate.
