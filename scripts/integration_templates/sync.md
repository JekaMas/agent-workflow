Inspect each delta and corresponding main spec. Apply authorized additions/modifications/removals while preserving unrelated requirements and full modified requirement context. Validate the affected specs and inspect the diff. Do not change product acceptance or implement unrelated behavior.

Resolve `openspec status --change <name> --json` first. Use returned
`planningHome.root` for main specs and `artifactPaths.specs.existingOutputPaths`
for delta files; preserve selected-root flags and any caller-selected exact
subset. Report an invalid selected path and stop before writes; do not silently discard
it. An empty set performs no writes.
Before writing, retrieve one current `openspec instructions specs --change <name>
--json` response, or reuse a valid snapshot supplied by archive. Failed/invalid
lookup blocks writes; omitted rules in a valid response means no configured rules.
Apply content rules without changing root, scope or selection. Handle ADDED,
MODIFIED, REMOVED and RENAMED requirements explicitly. Store-backed writes need
authority for the returned root. Retain full modified requirement/scenario content
and preserve unrelated requirements. There is no `instructions sync` operation.

After merging, resolve retained links from the main-spec location. Keep
change-specific execution notes in change evidence rather than copying dangling
relative links or premature completion claims into durable requirements.
